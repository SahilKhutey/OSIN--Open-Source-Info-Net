from typing import Dict, List, Optional, Any, Generator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
import time
import snscrape.modules.twitter as sntwitter
import tweepy
from kafka import KafkaProducer
import json
import logging
import hashlib
from .optimization import TwitterPerformanceOptimizer, AdaptiveSearchStrategy
from .monitoring import TwitterMetricsCollector

@dataclass
class TwitterConfig:
    """Twitter ingestion configuration"""
    # snscrape configuration
    snscrape_enabled: bool = True
    search_queries: List[str] = field(default_factory=lambda: [
        "breaking news", "emergency", "crisis", "disaster",
        "protest", "election", "summit", "trending",
        "earthquake", "fire", "flood", "storm"
    ])
    
    # Official API configuration
    api_enabled: bool = True
    bearer_token: Optional[str] = None
    api_keys: List[Dict] = field(default_factory=list)
    
    # Kafka configuration
    kafka_brokers: List[str] = field(default_factory=lambda: ['kafka:9092'])
    topic: str = "raw.twitter.posts"
    
    # Rate limiting
    requests_per_hour: int = 1000
    max_tweets_per_query: int = 1000

class MultiStrategyTwitterIngestor:
    """Multi-strategy Twitter data collection"""
    
    def __init__(self, config: TwitterConfig):
        self.config = config
        self.producer = KafkaProducer(
            bootstrap_servers=config.kafka_brokers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            batch_size=16384,
            linger_ms=10
        )
        self.deduplicator = TweetDeduplicator()
        self.rate_limiter = TwitterRateLimiter(config.requests_per_hour)
        
        # Initialize optimization components
        self.performance_optimizer = TwitterPerformanceOptimizer()
        self.search_strategy = AdaptiveSearchStrategy()
        
        # Initialize monitoring
        self.metrics = TwitterMetricsCollector()
        self.metrics.start_metrics_server()
        
        # Initialize API clients if enabled
        self.api_clients = []
        if config.api_enabled:
            self.api_clients = self._initialize_api_clients()
    
    def _initialize_api_clients(self) -> List[tweepy.Client]:
        """Initialize Twitter API clients"""
        
        clients = []
        
        for api_config in self.config.api_keys:
            try:
                client = tweepy.Client(
                    bearer_token=api_config.get('bearer_token'),
                    consumer_key=api_config.get('consumer_key'),
                    consumer_secret=api_config.get('consumer_secret'),
                    access_token=api_config.get('access_token'),
                    access_token_secret=api_config.get('access_token_secret')
                )
                clients.append(client)
            except Exception as e:
                logging.error(f"Failed to initialize API client: {e}")
        
        return clients
    
    async def start_ingestion(self):
        """Start multi-strategy ingestion"""
        
        logging.info("Starting Twitter multi-strategy ingestion")
        
        # Start snscrape streaming (if enabled)
        if self.config.snscrape_enabled:
            asyncio.create_task(self._snscrape_streaming())
        
        # Start API streaming (if enabled and clients available)
        if self.config.api_enabled and self.api_clients:
            asyncio.create_task(self._api_streaming())
        
        # Start search queries rotation
        asyncio.create_task(self._search_rotation())
        
        # Start performance optimization loop
        asyncio.create_task(self.performance_optimizer.optimize_ingestion(self))
    
    async def _snscrape_streaming(self):
        """Stream using snscrape (no API limits)"""
        
        while True:
            try:
                for query in self.config.search_queries:
                    if not self.rate_limiter.can_proceed('snscrape'):
                        await asyncio.sleep(self.rate_limiter.get_wait_time('snscrape'))
                    
                    scraper = sntwitter.TwitterSearchScraper(query)
                    tweet_count = 0
                    
                    for tweet in scraper.get_items():
                        if tweet_count >= self.config.max_tweets_per_query:
                            break
                        
                        processed_tweet = self._process_snscrape_tweet(tweet, query)
                        
                        # Deduplication check
                        if not self.deduplicator.is_duplicate(processed_tweet):
                            start_time = time.time()
                            self.producer.send(self.config.topic, processed_tweet)
                            latency = time.time() - start_time
                            self.metrics.record_tweet_processed('snscrape')
                            self.metrics.record_ingestion_latency('snscrape', latency)
                            tweet_count += 1
                        
                        # Rate limiting
                        if tweet_count % 100 == 0:
                            await asyncio.sleep(1)
                    
                    self.rate_limiter.record_request('snscrape')
                    await asyncio.sleep(5)  # Brief pause between queries
                
            except Exception as e:
                logging.error(f"snscrape streaming error: {e}")
                await asyncio.sleep(60)
    
    async def _api_streaming(self):
        """Stream using official Twitter API"""
        
        if not self.api_clients:
            return
        
        client = self.api_clients[0]  # Use first client, implement rotation later
        
        while True:
            try:
                # Sample API usage - would need proper streaming setup
                if not self.rate_limiter.can_proceed('api'):
                    await asyncio.sleep(self.rate_limiter.get_wait_time('api'))
                
                # Search recent tweets
                response = client.search_recent_tweets(
                    query="breaking news OR emergency OR crisis",
                    max_results=100,
                    tweet_fields=['created_at', 'public_metrics', 'context_annotations']
                )
                
                if response.data:
                    for tweet in response.data:
                        processed_tweet = self._process_api_tweet(tweet)
                        
                        if not self.deduplicator.is_duplicate(processed_tweet):
                            start_time = time.time()
                            self.producer.send(self.config.topic, processed_tweet)
                            latency = time.time() - start_time
                            self.metrics.record_tweet_processed('api')
                            self.metrics.record_ingestion_latency('api', latency)
                
                self.rate_limiter.record_request('api')
                if hasattr(response, 'meta'):
                    self.metrics.update_rate_limit('search_recent_tweets', response.meta.get('remaining', 0))
                await asyncio.sleep(300)  # 5 minutes between API calls
                
            except Exception as e:
                logging.error(f"API streaming error: {e}")
                self.metrics.record_error('api_error')
                await asyncio.sleep(300)
    
    async def _search_rotation(self):
        """Rotate through different search strategies"""
        
        # This could include:
        # - Trending topics discovery
        # - Geographic-specific searches
        # - User list monitoring
        # - Keyword expansion
        
        while True:
            # Update search queries based on trends and performance
            self.config.search_queries = await self.search_strategy.optimize_search_queries(
                self.config.search_queries
            )
            
            await asyncio.sleep(3600)  # Update hourly

    async def _discover_trending_topics(self) -> List[str]:
        """Placeholder for trending topics discovery logic"""
        # In a real implementation, this would call an API or scrape trends
        return []
    
    def _process_snscrape_tweet(self, tweet, query: str) -> Dict[str, Any]:
        """Process snscrape tweet into standardized format"""
        
        return {
            "platform": "twitter",
            "id": str(tweet.id),
            "text": tweet.rawContent,
            "user": {
                "id": str(tweet.user.id),
                "username": tweet.user.username,
                "display_name": tweet.user.displayname,
                "verified": tweet.user.verified,
                "followers": tweet.user.followersCount or 0
            },
            "engagement": {
                "likes": tweet.likeCount or 0,
                "retweets": tweet.retweetCount or 0,
                "replies": tweet.replyCount or 0,
                "quotes": tweet.quoteCount or 0
            },
            "metadata": {
                "created_at": tweet.date.isoformat(),
                "language": tweet.lang or "en",
                "source": "snscrape",
                "query_used": query,
                "url": tweet.url,
                "has_media": bool(tweet.media),
                "has_links": bool(tweet.outlinks)
            },
            "raw_data": {
                "conversation_id": str(tweet.conversationId),
                "retweeted_tweet": str(tweet.retweetedTweet.id) if tweet.retweetedTweet else None
            },
            "processing_metadata": {
                "collected_at": datetime.utcnow().isoformat(),
                "processing_version": "2.0"
            }
        }
    
    def _process_api_tweet(self, tweet) -> Dict[str, Any]:
        """Process official API tweet into standardized format"""
        
        return {
            "platform": "twitter",
            "id": tweet.id,
            "text": tweet.text,
            "user": {
                "id": tweet.author_id or "unknown"
            },
            "engagement": {
                "likes": tweet.public_metrics.get('like_count', 0),
                "retweets": tweet.public_metrics.get('retweet_count', 0),
                "replies": tweet.public_metrics.get('reply_count', 0),
                "quotes": tweet.public_metrics.get('quote_count', 0)
            },
            "metadata": {
                "created_at": tweet.created_at.isoformat() if tweet.created_at else datetime.utcnow().isoformat(),
                "source": "official_api",
                "context_annotations": getattr(tweet, 'context_annotations', [])
            },
            "processing_metadata": {
                "collected_at": datetime.utcnow().isoformat(),
                "processing_version": "2.0"
            }
        }

class TweetDeduplicator:
    """Advanced tweet deduplication"""
    
    def __init__(self, cache_size: int = 100000):
        self.seen_tweets = set()
        self.cache_size = cache_size
        
    def is_duplicate(self, tweet: Dict) -> bool:
        """Check if tweet is a duplicate"""
        
        tweet_hash = self._generate_tweet_hash(tweet)
        
        if tweet_hash in self.seen_tweets:
            return True
        
        self.seen_tweets.add(tweet_hash)
        
        # Maintain cache size
        if len(self.seen_tweets) > self.cache_size:
            self._clean_cache()
        
        return False
    
    def _generate_tweet_hash(self, tweet: Dict) -> str:
        """Generate unique hash for tweet"""
        
        # Use text + timestamp for deduplication
        content = f"{tweet['id']}_{tweet['text'][:200]}_{tweet['metadata']['created_at'][:10]}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _clean_cache(self):
        """Clean cache to maintain size"""
        
        # Convert to list, take last N elements
        items = list(self.seen_tweets)
        self.seen_tweets = set(items[-self.cache_size:])

class TwitterRateLimiter:
    """Twitter-specific rate limiting"""
    
    def __init__(self, requests_per_hour: int):
        self.limits = {
            'snscrape': requests_per_hour,
            'api': 300  # Twitter API limits
        }
        self.request_history = {
            'snscrape': [],
            'api': []
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
        
        # Find when the oldest request will expire
        oldest = min(self.request_history[method])
        wait_until = oldest + timedelta(hours=1)
        
        return max(0.0, (wait_until - datetime.utcnow()).total_seconds())
    
    def _clean_old_requests(self, method: str):
        """Remove requests older than 1 hour"""
        
        cutoff = datetime.utcnow() - timedelta(hours=1)
        self.request_history[method] = [
            t for t in self.request_history[method] 
            if t > cutoff
        ]

# Kafka Connect Twitter Integration
KAFKA_CONNECT_CONFIG = """
# jcustenborder/kafka-connect-twitter configuration
connector.class=com.github.jcustenborder.kafka.connect.twitter.TwitterSourceConnector
tasks.max=1
twitter.oauth.consumerKey=${CONSUMER_KEY}
twitter.oauth.consumerSecret=${CONSUMER_SECRET}
twitter.oauth.accessToken=${ACCESS_TOKEN}
twitter.oauth.accessTokenSecret=${ACCESS_TOKEN_SECRET}
topic=raw.twitter.posts
process.deletes=false
filter.keywords=breaking,news,emergency,crisis,disaster
kafka.status.interval.ms=10000
"""

# Docker deployment for Twitter ingestion
TWITTER_DOCKER_COMPOSE = """
version: '3.8'

services:
  twitter-snscrape:
    build: ./ingestion/twitter/snscrape
    environment:
      KAFKA_BROKERS: kafka:9092
      SEARCH_QUERIES: "breaking news,emergency,crisis,disaster"
    depends_on:
      - kafka
  
  twitter-api:
    build: ./ingestion/twitter/api
    environment:
      KAFKA_BROKERS: kafka:9092
      BEARER_TOKEN: ${TWITTER_BEARER_TOKEN}
    depends_on:
      - kafka
  
  kafka-connect-twitter:
    image: jcustenborder/kafka-connect-twitter:latest
    environment:
      CONSUMER_KEY: ${TWITTER_CONSUMER_KEY}
      CONSUMER_SECRET: ${TWITTER_CONSUMER_SECRET}
      ACCESS_TOKEN: ${TWITTER_ACCESS_TOKEN}
      ACCESS_TOKEN_SECRET: ${TWITTER_ACCESS_TOKEN_SECRET}
    depends_on:
      - kafka
      - schema-registry
"""

if __name__ == "__main__":
    config = TwitterConfig(
        snscrape_enabled=True,
        api_enabled=True,
        search_queries=[
            "breaking news", "emergency", "crisis", "disaster",
            "protest", "election", "summit", "trending"
        ]
    )
    
    ingestor = MultiStrategyTwitterIngestor(config)
    asyncio.run(ingestor.start_ingestion())
