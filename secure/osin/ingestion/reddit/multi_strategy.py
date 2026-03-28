from typing import Dict, List, Optional, Any, Generator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
import praw
from kafka import KafkaProducer
import json
import logging
import hashlib
import feedparser
import requests
import time
from .monitoring import RedditMetricsCollector
from .advanced_features import SubredditIntelligence

@dataclass
class RedditConfig:
    """Reddit ingestion configuration"""
    # PRAW API configuration
    praw_enabled: bool = True
    client_configs: List[Dict] = field(default_factory=lambda: [
        {
            'client_id': 'CLIENT_ID_1',
            'client_secret': 'CLIENT_SECRET_1',
            'user_agent': 'osin_reddit_ingestor_v1'
        }
    ])
    
    # Kafka Connect configuration
    kafka_connect_enabled: bool = True
    
    # Pushshift configuration (historical data)
    pushshift_enabled: bool = True
    pushshift_base_url: str = "https://api.pushshift.io"
    
    # RSS configuration
    rss_enabled: bool = True
    rss_feeds: List[str] = field(default_factory=lambda: [
        "https://www.reddit.com/r/worldnews/.rss",
        "https://www.reddit.com/r/news/.rss",
        "https://www.reddit.com/r/politics/.rss"
    ])
    
    # Subreddit monitoring
    monitored_subreddits: List[str] = field(default_factory=lambda: [
        'worldnews', 'news', 'politics', 'economics',
        'technology', 'science', 'environment', 'climate',
        'cybersecurity', 'programming', 'futurology',
        'breakingnews', 'crisis', 'emergency'
    ])
    
    # Kafka configuration
    kafka_brokers: List[str] = field(default_factory=lambda: ['kafka:9092'])
    topics: Dict[str, str] = field(default_factory=lambda: {
        'submissions': 'raw.reddit.submissions',
        'comments': 'raw.reddit.comments',
        'rss': 'raw.reddit.rss'
    })
    
    # Rate limiting
    requests_per_minute: int = 60  # Reddit API limits

class MultiStrategyRedditIngestor:
    """Multi-strategy Reddit data collection"""
    
    def __init__(self, config: RedditConfig):
        self.config = config
        self.producer = KafkaProducer(
            bootstrap_servers=config.kafka_brokers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            batch_size=16384,
            linger_ms=10,
            compression_type='snappy'
        )
        self.deduplicator = RedditDeduplicator()
        self.rate_limiter = RedditRateLimiter(config.requests_per_minute)
        
        # Initialize monitoring
        self.metrics = RedditMetricsCollector()
        self.metrics.start_metrics_server()
        
        # Initialize advanced intelligence
        self.intelligence = SubredditIntelligence()
        
        # Initialize PRAW clients
        self.praw_clients = []
        if config.praw_enabled:
            self.praw_clients = self._initialize_praw_clients()
    
    def _initialize_praw_clients(self) -> List[praw.Reddit]:
        """Initialize PRAW Reddit clients"""
        
        clients = []
        
        for client_config in self.config.client_configs:
            try:
                client = praw.Reddit(
                    client_id=client_config['client_id'],
                    client_secret=client_config['client_secret'],
                    user_agent=client_config['user_agent']
                )
                clients.append(client)
            except Exception as e:
                logging.error(f"Failed to initialize PRAW client: {e}")
        
        return clients
    
    async def start_ingestion(self):
        """Start multi-strategy Reddit ingestion"""
        
        logging.info("Starting Reddit multi-strategy ingestion")
        
        # Start PRAW streaming (if enabled)
        if self.config.praw_enabled and self.praw_clients:
            asyncio.create_task(self._praw_streaming())
        
        # Start RSS monitoring (if enabled)
        if self.config.rss_enabled:
            asyncio.create_task(self._rss_monitoring())
        
        # Start Pushshift historical collection (if enabled)
        if self.config.pushshift_enabled:
            asyncio.create_task(self._pushshift_historical())
    
    async def _praw_streaming(self):
        """Stream Reddit data using PRAW"""
        
        while True:
            try:
                for subreddit_name in self.config.monitored_subreddits:
                    if not self.rate_limiter.can_proceed('praw'):
                        await asyncio.sleep(self.rate_limiter.get_wait_time('praw'))
                    
                    if not self.praw_clients:
                        break
                    
                    client = self.praw_clients[0]  # Implement client rotation
                    
                    # Stream new submissions
                    await self._stream_subreddit_submissions(client, subreddit_name)
                    
                    # Stream comments (for high-traffic subreddits)
                    if subreddit_name in ['worldnews', 'news', 'politics']:
                        await self._stream_subreddit_comments(client, subreddit_name)
                    
                    # Periodic advanced analysis
                    if len(self.config.monitored_subreddits) > 0:
                        # In a real scenario, would fetch recent data from Kafka/DB
                        # Using empty list for now to demonstrate integration
                        health_analysis = await self.intelligence.analyze_subreddit_health(
                            subreddit_name, []
                        )
                        logging.info(f"Subreddit Health Analysis for {subreddit_name}: {health_analysis}")
                    
                    self.rate_limiter.record_request('praw')
                    await asyncio.sleep(2)  # Brief pause between subreddits
                
                await asyncio.sleep(30)  # Wait before next cycle
                
            except Exception as e:
                logging.error(f"PRAW streaming error: {e}")
                await asyncio.sleep(60)
    
    async def _stream_subreddit_submissions(self, client: praw.Reddit, subreddit_name: str):
        """Stream submissions from a subreddit"""
        
        try:
            subreddit = client.subreddit(subreddit_name)
            
            for submission in subreddit.stream.submissions(skip_existing=True):
                if submission is None:
                    continue
                
                processed_submission = self._process_praw_submission(submission, subreddit_name)
                
                # Deduplication check
                if not self.deduplicator.is_duplicate(processed_submission):
                    start_time = time.time()
                    self.producer.send(self.config.topics['submissions'], processed_submission)
                    latency = time.time() - start_time
                    self.metrics.record_submission_processed(subreddit_name)
                    self.metrics.record_ingestion_latency('submission', latency)
                
                # Rate limiting check
                if not self.rate_limiter.can_proceed('praw'):
                    await asyncio.sleep(self.rate_limiter.get_wait_time('praw'))
                
        except Exception as e:
            logging.error(f"Error streaming submissions from {subreddit_name}: {e}")
            raise
    
    async def _stream_subreddit_comments(self, client: praw.Reddit, subreddit_name: str):
        """Stream comments from a subreddit"""
        
        try:
            subreddit = client.subreddit(subreddit_name)
            
            for comment in subreddit.stream.comments(skip_existing=True):
                if comment is None:
                    continue
                
                processed_comment = self._process_praw_comment(comment, subreddit_name)
                
                if not self.deduplicator.is_duplicate(processed_comment):
                    start_time = time.time()
                    self.producer.send(self.config.topics['comments'], processed_comment)
                    latency = time.time() - start_time
                    self.metrics.record_comment_processed(subreddit_name)
                    self.metrics.record_ingestion_latency('comment', latency)
                
                if not self.rate_limiter.can_proceed('praw'):
                    await asyncio.sleep(self.rate_limiter.get_wait_time('praw'))
                
        except Exception as e:
            logging.error(f"Error streaming comments from {subreddit_name}: {e}")
    
    async def _rss_monitoring(self):
        """Monitor Reddit via RSS feeds"""
        
        while True:
            try:
                for rss_url in self.config.rss_feeds:
                    if not self.rate_limiter.can_proceed('rss'):
                        await asyncio.sleep(self.rate_limiter.get_wait_time('rss'))
                    
                    feed = feedparser.parse(rss_url)
                    
                    for entry in feed.entries:
                        processed_entry = self._process_rss_entry(entry)
                        
                        if not self.deduplicator.is_duplicate(processed_entry):
                            self.producer.send(self.config.topics['rss'], processed_entry)
                    
                    self.rate_limiter.record_request('rss')
                    await asyncio.sleep(1)
                
                await asyncio.sleep(300)  # Wait 5 minutes between RSS cycles
                
            except Exception as e:
                logging.error(f"RSS monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _pushshift_historical(self):
        """Collect historical data using Pushshift API"""
        
        while True:
            try:
                # Collect historical data for analysis
                for subreddit in self.config.monitored_subreddits:
                    historical_data = await self._fetch_pushshift_data(subreddit)
                    
                    for item in historical_data:
                        processed_item = self._process_pushshift_item(item)
                        
                        if not self.deduplicator.is_duplicate(processed_item):
                            self.producer.send(self.config.topics['submissions'], processed_item)
                
                # Historical collection runs less frequently
                await asyncio.sleep(3600)  # Wait 1 hour
                
            except Exception as e:
                logging.error(f"Pushshift historical collection error: {e}")
                await asyncio.sleep(300)

    async def _fetch_pushshift_data(self, subreddit: str, hours_back: int = 24) -> List[Dict]:
        """Fetch historical Reddit data via Pushshift API"""
        try:
            after_timestamp = int(time.time()) - (hours_back * 3600)
            url = f"{self.config.pushshift_base_url}/reddit/search/submission/"
            params = {
                'subreddit': subreddit,
                'after': after_timestamp,
                'size': 1000,
                'sort': 'desc',
                'sort_type': 'created_utc'
            }
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json().get('data', [])
            return []
        except Exception as e:
            logging.error(f"Pushshift fetch error: {e}")
            return []
    
    def _process_praw_submission(self, submission, subreddit_name: str) -> Dict[str, Any]:
        """Process PRAW submission into standardized format"""
        
        return {
            "platform": "reddit",
            "type": "submission",
            "id": submission.id,
            "title": submission.title,
            "text": submission.selftext,
            "author": str(submission.author) if submission.author else "[deleted]",
            "subreddit": subreddit_name,
            "engagement": {
                "score": submission.score,
                "upvote_ratio": submission.upvote_ratio,
                "num_comments": submission.num_comments,
                "total_awards": submission.total_awards_received
            },
            "metadata": {
                "created_utc": submission.created_utc,
                "url": submission.url,
                "permalink": submission.permalink,
                "nsfw": submission.over_18,
                "spoiler": submission.spoiler,
                "locked": submission.locked,
                "stickied": submission.stickied
            },
            "content_metadata": {
                "domain": submission.domain,
                "is_self": submission.is_self,
                "is_video": submission.is_video,
                "media_only": submission.media_only
            },
            "processing_metadata": {
                "collected_at": datetime.utcnow().isoformat(),
                "source": "praw",
                "processing_version": "2.0"
            }
        }
    
    def _process_praw_comment(self, comment, subreddit_name: str) -> Dict[str, Any]:
        """Process PRAW comment"""
        
        return {
            "platform": "reddit",
            "type": "comment",
            "id": comment.id,
            "text": comment.body,
            "author": str(comment.author) if comment.author else "[deleted]",
            "submission_id": comment.submission.id if comment.submission else None,
            "subreddit": subreddit_name,
            "engagement": {
                "score": comment.score,
                "total_awards": comment.total_awards_received,
                "controversiality": comment.controversiality
            },
            "metadata": {
                "created_utc": comment.created_utc,
                "permalink": comment.permalink,
                "is_submitter": comment.is_submitter,
                "stickied": comment.stickied
            },
            "processing_metadata": {
                "collected_at": datetime.utcnow().isoformat(),
                "source": "praw",
                "processing_version": "2.0"
            }
        }
    
    def _process_rss_entry(self, entry) -> Dict[str, Any]:
        """Process RSS entry"""
        
        return {
            "platform": "reddit",
            "type": "rss_submission",
            "id": entry.id,
            "title": entry.title,
            "summary": entry.summary if hasattr(entry, 'summary') else '',
            "author": entry.author if hasattr(entry, 'author') else '',
            "metadata": {
                "published": entry.published if hasattr(entry, 'published') else '',
                "link": entry.link,
                "source": "rss"
            },
            "processing_metadata": {
                "collected_at": datetime.utcnow().isoformat(),
                "processing_version": "2.0"
            }
        }

    def _process_pushshift_item(self, item: Dict) -> Dict[str, Any]:
        """Process Pushshift item"""
        return {
            "platform": "reddit",
            "type": "historical_submission",
            "id": item.get('id'),
            "title": item.get('title'),
            "text": item.get('selftext', ''),
            "author": item.get('author'),
            "subreddit": item.get('subreddit'),
            "metadata": {
                "created_utc": item.get('created_utc'),
                "url": item.get('url'),
                "permalink": item.get('permalink')
            },
            "processing_metadata": {
                "collected_at": datetime.utcnow().isoformat(),
                "source": "pushshift",
                "processing_version": "2.0"
            }
        }

class RedditDeduplicator:
    """Advanced Reddit content deduplication"""
    
    def __init__(self, cache_size: int = 100000):
        self.seen_content = set()
        self.cache_size = cache_size
        
    def is_duplicate(self, content: Dict) -> bool:
        """Check if content is a duplicate"""
        
        content_hash = self._generate_content_hash(content)
        
        if content_hash in self.seen_content:
            return True
        
        self.seen_content.add(content_hash)
        
        # Maintain cache size
        if len(self.seen_content) > self.cache_size:
            self._clean_cache()
        
        return False
    
    def _generate_content_hash(self, content: Dict) -> str:
        """Generate unique hash for content"""
        
        # Use ID + title/text for deduplication
        text_content = content.get('title', '') + content.get('text', '')[:100]
        content_id = content.get('id', '')
        
        normalized = f"{content_id}_{text_content}".lower()
        return hashlib.sha256(normalized.encode()).hexdigest()
    
    def _clean_cache(self):
        """Clean cache to maintain size"""
        
        items = list(self.seen_content)
        self.seen_content = set(items[-self.cache_size:])

class RedditRateLimiter:
    """Reddit-specific rate limiting"""
    
    def __init__(self, requests_per_minute: int):
        self.limits = {
            'praw': requests_per_minute,
            'rss': 100,  # RSS is less restrictive
            'pushshift': 60  # Pushshift has its own limits
        }
        self.request_history = {
            'praw': [],
            'rss': [],
            'pushshift': []
        }
    
    def can_proceed(self, method: str) -> bool:
        """Check if request can proceed"""
        
        self._clean_old_requests(method)
        return len(self.request_history[method]) < self.limits[method]
    
    def record_request(self, method: str):
        """Record a request"""
        
        self.request_history[method].append(datetime.utcnow())
    
    def get_wait_time(self, method: str) -> float:
        """Get time to wait until next request"""
        
        self._clean_old_requests(method)
        
        if len(self.request_history[method]) < self.limits[method]:
            return 0.0
        
        # Find when the oldest request will expire (1 minute window)
        oldest = min(self.request_history[method])
        wait_until = oldest + timedelta(minutes=1)
        
        return max(0.0, (wait_until - datetime.utcnow()).total_seconds())
    
    def _clean_old_requests(self, method: str):
        """Remove requests older than 1 minute"""
        
        cutoff = datetime.utcnow() - timedelta(minutes=1)
        self.request_history[method] = [
            t for t in self.request_history[method] 
            if t > cutoff
        ]

if __name__ == "__main__":
    config = RedditConfig()
    ingestor = MultiStrategyRedditIngestor(config)
    asyncio.run(ingestor.start_ingestion())
