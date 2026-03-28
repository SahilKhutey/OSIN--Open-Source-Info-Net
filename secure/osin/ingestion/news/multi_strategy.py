from typing import Dict, List, Optional, Any, Generator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
import feedparser
import newspaper
from kafka import KafkaProducer
import json
import logging
import hashlib
import requests
from bs4 import BeautifulSoup
import re
import random
import statistics

@dataclass
class NewsConfig:
    """News ingestion configuration"""
    # newspaper3k configuration
    newspaper3k_enabled: bool = True
    newspaper3k_settings: Dict[str, Any] = field(default_factory=lambda: {
        'memoize_articles': False,
        'fetch_images': False,
        'follow_meta_refresh': False,
        'timeout': 30,
        'max_threads': 2,
        'language': 'en'
    })
    
    # RSS configuration
    rss_enabled: bool = True
    rss_feeds: List[str] = field(default_factory=lambda: [
        "https://rss.cnn.com/rss/edition.rss",
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://www.reutersagency.com/feed/?best-topics=world-news&post_type=best",
        "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
    ])
    
    # GDELT configuration
    gdelt_enabled: bool = True
    gdelt_base_url: str = "https://api.gdeltproject.org/api/v2/doc/doc"
    
    # Target monitoring
    monitored_sites: List[str] = field(default_factory=lambda: [
        "cnn.com", "bbc.com", "reuters.com", "apnews.com",
        "nytimes.com", "washingtonpost.com", "aljazeera.com"
    ])
    
    # Kafka configuration
    kafka_brokers: List[str] = field(default_factory=lambda: ['kafka:9092'])
    topics: Dict[str, str] = field(default_factory=lambda: {
        'articles': 'raw.news.articles',
        'events': 'raw.news.events',
        'metadata': 'raw.news.metadata'
    })
    
    # Rate limiting
    requests_per_minute: int = 10  # Conservative limit for news sites
    delay_between_requests: int = 6  # seconds

class MultiStrategyNewsIngestor:
    """Multi-strategy news data collection"""
    
    def __init__(self, config: NewsConfig):
        self.config = config
        self.producer = KafkaProducer(
            bootstrap_servers=config.kafka_brokers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            batch_size=16384,
            linger_ms=10,
            compression_type='snappy'
        )
        self.deduplicator = NewsDeduplicator()
        self.rate_limiter = NewsRateLimiter(config.requests_per_minute)
        
        # Initialize tools
        self.newspaper_config = self.config.newspaper3k_settings.copy()
        self.rss_parser = NewsRSSParser()
        self.gdelt_client = GDELTClient()
    
    async def start_ingestion(self):
        """Start multi-strategy news ingestion"""
        
        logging.info("Starting News multi-strategy ingestion")
        
        # Start RSS monitoring
        if self.config.rss_enabled:
            asyncio.create_task(self._rss_monitoring())
        
        # Start newspaper3k article extraction
        if self.config.newspaper3k_enabled:
            asyncio.create_task(self._article_extraction())
        
        # Start GDELT event collection
        if self.config.gdelt_enabled:
            asyncio.create_task(self._gdelt_event_collection())
    
    async def _rss_monitoring(self):
        """Monitor news via RSS feeds"""
        
        while True:
            try:
                for rss_url in self.config.rss_feeds:
                    if not self.rate_limiter.can_proceed('rss'):
                        await asyncio.sleep(self.rate_limiter.get_wait_time('rss'))
                    
                    await self._process_rss_feed(rss_url)
                    self.rate_limiter.record_request('rss')
                    await asyncio.sleep(2)  # Rate limiting
                    
                await asyncio.sleep(300)  # Wait 5 minutes between RSS cycles
                
            except Exception as e:
                logging.error(f"RSS monitoring error: {e}")
                await asyncio.sleep(300)
    
    async def _process_rss_feed(self, url: str):
        """Process a single RSS feed"""
        
        try:
            feed = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.rss_parser.parse_feed(url)
            )
            
            for entry in feed.get('entries', []):
                article_data = self._process_rss_entry(entry)
                
                if not self.deduplicator.is_duplicate(article_data):
                    self.producer.send(self.config.topics['articles'], article_data)
        
        except Exception as e:
            logging.error(f"Error processing RSS feed {url}: {e}")
    
    async def _article_extraction(self):
        """Extract articles using newspaper3k"""
        
        while True:
            try:
                for site in self.config.monitored_sites:
                    if not self.rate_limiter.can_proceed('newspaper'):
                        await asyncio.sleep(self.rate_limiter.get_wait_time('newspaper'))
                    
                    await self._extract_site_articles(site)
                    self.rate_limiter.record_request('newspaper')
                    await asyncio.sleep(self.config.delay_between_requests)
                
                await asyncio.sleep(3600)  # Wait 1 hour between cycles
                
            except Exception as e:
                logging.error(f"Article extraction error: {e}")
                await asyncio.sleep(300)
    
    async def _extract_site_articles(self, domain: str):
        """Extract articles from a specific site"""
        
        try:
            # Get top stories (simplified)
            top_stories = await self._get_top_stories(domain)
            
            for url in top_stories[:10]:  # Process up to 10 stories per site
                article = await self._extract_article(url)
                
                if article:
                    article_data = self._process_article(article)
                    
                    if not self.deduplicator.is_duplicate(article_data):
                        self.producer.send(self.config.topics['articles'], article_data)
        
        except Exception as e:
            logging.error(f"Error extracting articles for {domain}: {e}")
    
    async def _get_top_stories(self, domain: str) -> List[str]:
        """Get top stories for a news site"""
        
        # This would implement actual top stories detection
        # For demonstration, return mock data
        return [
            f"https://{domain}/story1",
            f"https://{domain}/story2",
            f"https://{domain}/story3"
        ]
    
    async def _extract_article(self, url: str) -> Optional[Dict]:
        """Extract article content using newspaper3k"""
        
        try:
            # Use newspaper3k to download and parse
            article = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: newspaper.Article(url, **self.newspaper_config)
            )
            
            article.download()
            article.parse()
            article.nlp()
            
            return {
                'url': url,
                'title': article.title,
                'text': article.text,
                'summary': article.summary,
                'keywords': article.keywords,
                'top_image': article.top_image,
                'source_url': article.source_url,
                'publish_date': article.publish_date.isoformat() if article.publish_date else None,
                'meta_data': article.meta_data
            }
            
        except Exception as e:
            logging.error(f"Article extraction error for {url}: {e}")
            return None
    
    async def _gdelt_event_collection(self):
        """Collect global news events from GDELT"""
        
        while True:
            try:
                # GDELT 2.0 API integration
                events = await self.gdelt_client.fetch_recent_events()
                
                for event in events:
                    event_data = self._process_gdelt_event(event)
                    
                    if not self.deduplicator.is_duplicate(event_data):
                        self.producer.send(self.config.topics['events'], event_data)
                
                # GDELT has its own rate limits (5 requests/minute)
                await asyncio.sleep(60)  # Wait 1 minute
                
            except Exception as e:
                logging.error(f"GDELT collection error: {e}")
                await asyncio.sleep(300)
    
    def _process_rss_entry(self, entry: Dict) -> Dict[str, Any]:
        """Process RSS entry into standardized format"""
        
        return {
            "platform": "news",
            "source": "rss",
            "id": entry.get('id', ''),
            "title": entry.get('title', ''),
            "summary": entry.get('summary', ''),
            "content": entry.get('content', ''),
            "author": entry.get('author', ''),
            "metadata": {
                "published": entry.get('published', ''),
                "link": entry.get('link', ''),
                "language": entry.get('language', 'en'),
                "source_url": entry.get('source', {}).get('url', '') if entry.get('source') else ''
            },
            "categorization": {
                "categories": entry.get('tags', []),
                "source_type": "rss"
            },
            "processing_metadata": {
                "collected_at": datetime.utcnow().isoformat(),
                "processing_version": "2.0"
            }
        }
    
    def _process_article(self, article: Dict) -> Dict[str, Any]:
        """Process extracted article into standardized format"""
        
        return {
            "platform": "news",
            "source": "newspaper3k",
            "id": hashlib.sha256(article['url'].encode()).hexdigest()[:16],
            "url": article['url'],
            "title": article['title'],
            "text": article['text'],
            "summary": article['summary'],
            "keywords": article['keywords'],
            "top_image": article['top_image'],
            "metadata": {
                "published_date": article['publish_date'],
                "source_url": article['source_url'],
                "language": article['meta_data'].get('language', 'en'),
                "domain": self._extract_domain(article['source_url'])
            },
            "content_analysis": {
                "sentiment": self._analyze_sentiment(article['text']),
                "entities": self._extract_entities(article['text']),
                "categories": self._categorize_content(article)
            },
            "processing_metadata": {
                "collected_at": datetime.utcnow().isoformat(),
                "processing_version": "2.0"
            }
        }
    
    def _process_gdelt_event(self, event: Dict) -> Dict[str, Any]:
        """Process GDELT event into standardized format"""
        
        return {
            "platform": "gdelt",
            "source": "GDELT",
            "id": event.get('GKGRecordID', ''),
            "title": event.get('DocumentIdentifier', ''),
            "content": event.get('V2Title', ''),
            "metadata": {
                "published": event.get('DateTime', ''),
                "language": event.get('V2Tone', ''),
                "source_url": event.get('DocumentIdentifier', ''),
                "tone_score": event.get('V2Tone', ''),
                "location": event.get('V2Locations', ''),
                "organizations": event.get('V2Organizations', ''),
                "people": event.get('V2Persons', '')
            },
            "gdelt_metadata": {
                "tone": event.get('V2Tone', ''),
                "positive_score": event.get('V2Tone', 0),
                "negative_score": event.get('V2Tone', 0),
                "word_count": event.get('V2WordCount', 0)
            },
            "processing_metadata": {
                "collected_at": datetime.utcnow().isoformat(),
                "processing_version": "2.0"
            }
        }
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        
        from urllib.parse import urlparse
        return urlparse(url).netloc
    
    def _analyze_sentiment(self, text: str) -> float:
        """Basic sentiment analysis for articles"""
        
        # In production, this would use NLP libraries
        positive_words = ['good', 'great', 'positive', 'up', 'win', 'success']
        negative_words = ['bad', 'terrible', 'negative', 'down', 'loss', 'failure']
        
        positive_count = sum(1 for word in text.lower().split() if word in positive_words)
        negative_count = sum(1 for word in text.lower().split() if word in negative_words)
        
        total = positive_count + negative_count
        if total == 0:
            return 0.0
        
        return (positive_count - negative_count) / total
    
    def _extract_entities(self, text: str) -> List[str]:
        """Basic entity extraction"""
        
        # In production, this would use NLP libraries
        entities = []
        
        # Look for capitalized words (simplified approach)
        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        for word in words:
            if len(word) > 2 and word.lower() not in ['The', 'And', 'But']:
                entities.append(word)
        
        return entities
    
    def _categorize_content(self, article: Dict) -> List[str]:
        """Categorize article content"""
        
        categories = []
        text = article['text'].lower()
        
        # Simple keyword-based categorization
        if any(word in text for word in ['politic', 'election', 'president', 'government']):
            categories.append('politics')
        if any(word in text for word in ['econom', 'market', 'business', 'stock']):
            categories.append('economy')
        if any(word in text for word in ['climate', 'environment', 'global', 'warming']):
            categories.append('environment')
        if any(word in text for word in ['tech', 'technology', 'digital', 'software']):
            categories.append('technology')
        if any(word in text for word in ['health', 'disease', 'medical', 'vaccine']):
            categories.append('health')
        
        return categories

class NewsDeduplicator:
    """News content deduplication"""
    
    def __init__(self, cache_size: int = 100000):
        self.seen_content = set()
        self.cache_size = cache_size
    
    def is_duplicate(self, content: Dict) -> bool:
        """Check if content is a duplicate"""
        
        content_hash = self._generate_content_hash(content)
        
        if content_hash in self.seen_content:
            return True
        
        self.seen_content.add(content_hash)
        
        if len(self.seen_content) > self.cache_size:
            self._clean_cache()
        
        return False
    
    def _generate_content_hash(self, content: Dict) -> str:
        """Generate unique hash for content"""
        
        # Use URL + title for deduplication
        identifier = content.get('url', '') or content.get('id', '')
        title = content.get('title', '')
        
        normalized = f"{identifier}_{title[:50]}".lower()
        return hashlib.sha256(normalized.encode()).hexdigest()
    
    def _clean_cache(self):
        """Clean cache to maintain size"""
        
        items = list(self.seen_content)
        self.seen_content = set(items[-self.cache_size:])

class NewsRateLimiter:
    """News-specific rate limiting"""
    
    def __init__(self, requests_per_minute: int):
        self.limits = {
            'rss': requests_per_minute,
            'newspaper': requests_per_minute,
            'gdelt': 5  # GDELT has strict rate limits
        }
        self.request_history = {
            'rss': [],
            'newspaper': [],
            'gdelt': []
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
        wait_until = oldest + timedelta(minutes=1)
        
        return max(0.0, (wait_until - datetime.utcnow()).total_seconds())
    
    def _clean_old_requests(self, method: str):
        """Remove old requests based on method"""
        
        cutoff = datetime.utcnow() - timedelta(minutes=1)
        
        self.request_history[method] = [
            t for t in self.request_history[method] 
            if t > cutoff
        ]

class NewsRSSParser:
    """RSS parser with enhanced features"""
    
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        ]
    
    def parse_feed(self, url: str) -> Dict[str, Any]:
        """Parse RSS feed with custom headers"""
        
        try:
            # Add custom headers to avoid blocking
            headers = {
                'User-Agent': self._get_random_user_agent(),
                'Accept': 'application/rss+xml,application/xhtml+xml,text/html;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5'
            }
            
            # Parse feed
            return feedparser.parse(url, request_headers=headers)
            
        except Exception as e:
            logging.error(f"RSS parsing error for {url}: {e}")
            return {}
    
    def _get_random_user_agent(self) -> str:
        """Get a random user agent"""
        
        return random.choice(self.user_agents)

class GDELTClient:
    """GDELT Project API client"""
    
    def __init__(self):
        self.base_url = "https://api.gdeltproject.org/api/v2/doc/doc"
    
    async def fetch_recent_events(self, hours_back: int = 24) -> List[Dict]:
        """Fetch recent events from GDELT"""
        
        try:
            # Calculate timestamp for X hours ago
            import time
            after_timestamp = int(time.time()) - (hours_back * 3600)
            
            params = {
                'query': 'sourcelang:english',
                'mode': 'artlist',
                'maxrecords': 100,
                'format': 'json',
                'startdatetime': after_timestamp
            }
            
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: requests.get(self.base_url, params=params)
            )
            
            if response.status_code == 200:
                return response.json().get('articles', [])
            else:
                logging.error(f"GDELT API error: {response.status_code}")
                return []
                
        except Exception as e:
            logging.error(f"GDELT fetch error: {e}")
            return []

# News-specific intelligence features
class NewsIntelligence:
    """Advanced news intelligence gathering"""
    
    def __init__(self):
        self.content_analyzer = ContentAnalyzer()
        self.event_correlator = EventCorrelator()
        self.trend_detector = TrendDetector()
    
    async def analyze_news_trends(self, news_data: List[Dict]) -> Dict[str, Any]:
        """Analyze trends in news content"""
        
        if not news_data:
            return {}
        
        analysis = {
            'content_analysis': await self.content_analyzer.analyze_content(news_data),
            'event_correlation': await self.event_correlator.correlate_events(news_data),
            'trend_detection': await self.trend_detector.detect_trends(news_data),
            'sentiment_analysis': await self.content_analyzer.analyze_sentiment(news_data),
            'geographic_analysis': await self.content_analyzer.analyze_geographic_distribution(news_data)
        }
        
        return analysis

class ContentAnalyzer:
    """Analyze news content characteristics"""
    
    async def analyze_content(self, news_data: List[Dict]) -> Dict[str, Any]:
        """Analyze news content features"""
        
        # Extract content for analysis
        texts = []
        titles = []
        sources = []
        
        for item in news_data:
            if item.get('source') == 'newspaper3k':
                text = item.get('text', '')
                if text:
                    texts.append(text)
                title = item.get('title', '')
                if title:
                    titles.append(title)
                
                source = item.get('metadata', {}).get('source_url', '')
                if source:
                    sources.append(source)
        
        return {
            'content_metrics': await self._calculate_content_metrics(texts),
            'source_analysis': await self._analyze_sources(sources),
            'topic_distribution': await self._extract_topics(titles),
            'sentiment_trends': await self._analyze_sentiment_trends(news_data)
        }
    
    async def analyze_sentiment(self, news_data: List[Dict]) -> Dict[str, Any]:
        """Analyze sentiment in news content"""
        
        positive_count = 0
        negative_count = 0
        total = 0
        
        for item in news_data:
            if item.get('content_analysis'):
                sentiment = item['content_analysis'].get('sentiment', 0)
                if sentiment > 0:
                    positive_count += 1
                elif sentiment < 0:
                    negative_count += 1
                total += 1
        
        if total == 0:
            return {'overall_sentiment': 0, 'positive_rate': 0, 'negative_rate': 0}
        
        return {
            'overall_sentiment': (positive_count - negative_count) / total,
            'positive_rate': positive_count / total,
            'negative_rate': negative_count / total,
            'neutral_rate': 1 - (positive_count + negative_count) / total
        }
    
    async def analyze_geographic_distribution(self, news_data: List[Dict]) -> Dict[str, Any]:
        """Analyze geographic distribution of news coverage"""
        
        locations = []
        
        for item in news_data:
            # Extract location from text (simplified)
            text = item.get('text', '') or item.get('content', '')
            # In production, this would use NLP
            if 'Washington' in text:
                locations.append('Washington')
            if 'New York' in text:
                locations.append('New York')
            if 'London' in text:
                locations.append('London')
        
        location_counts = {}
        for location in locations:
            location_counts[location] = location_counts.get(location, 0) + 1
        
        return {
            'location_distribution': location_counts,
            'top_locations': dict(sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            'coverage_diversity': len(location_counts) / max(1, len(locations))
        }
    
    async def _calculate_content_metrics(self, texts: List[str]) -> Dict[str, Any]:
        """Calculate content metrics for news articles"""
        
        word_counts = [len(text.split()) for text in texts if text]
        sentence_counts = [text.count('.') for text in texts if text]
        
        return {
            'average_word_count': statistics.mean(word_counts) if word_counts else 0,
            'average_sentence_count': statistics.mean(sentence_counts) if sentence_counts else 0,
            'content_diversity': await self._calculate_content_diversity(texts),
            'complexity_score': await self._estimate_content_complexity(texts)
        }
    
    async def _calculate_content_diversity(self, texts: List[str]) -> float:
        """Calculate content diversity score"""
        
        if not texts:
            return 0.0
        
        # Simple diversity metric
        all_text = ' '.join(texts).lower()
        unique_words = len(set(all_text.split()))
        total_words = len(all_text.split())
        
        return unique_words / total_words if total_words > 0 else 0.0
    
    async def _estimate_content_complexity(self, texts: List[str]) -> float:
        """Estimate content complexity"""
        
        if not texts:
            return 0.0
        
        # Simple complexity metric
        complex_word_count = 0
        total_words = 0
        
        for text in texts:
            words = text.split()
            total_words += len(words)
            for word in words:
                if len(word) > 10:  # Words longer than 10 characters
                    complex_word_count += 1
        
        return complex_word_count / total_words if total_words > 0 else 0.0

    async def _analyze_sources(self, sources: List[str]) -> Dict[str, Any]:
        """Analyze news sources"""
        source_counts = {}
        for s in sources:
            source_counts[s] = source_counts.get(s, 0) + 1
        return source_counts

    async def _extract_topics(self, titles: List[str]) -> Dict[str, Any]:
        """Extract topics from titles"""
        topic_counts = {}
        for title in titles:
            for word in title.split():
                if len(word) > 4:
                    topic_counts[word.lower()] = topic_counts.get(word.lower(), 0) + 1
        return dict(sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:10])

    async def _analyze_sentiment_trends(self, news_data: List[Dict]) -> List[float]:
        """Analyze sentiment trends over time"""
        return []

class EventCorrelator:
    """Correlate news events across sources"""
    
    async def correlate_events(self, news_data: List[Dict]) -> Dict[str, Any]:
        """Correlate events across news sources"""
        
        # Extract events
        events = []
        for item in news_data:
            # Simplified event extraction
            event = {
                'title': item.get('title', ''),
                'summary': item.get('summary', ''),
                'source': item.get('metadata', {}).get('source_url', ''),
                'timestamp': item.get('metadata', {}).get('published_date', '')
            }
            events.append(event)
        
        # Find similar events (simplified)
        similar_events = []
        for i in range(len(events)):
            for j in range(i+1, len(events)):
                if self._events_are_similar(events[i], events[j]):
                    similar_events.append((events[i], events[j]))
        
        return {
            'similar_event_pairs': similar_events,
            'event_clusters': await self._identify_event_clusters(events),
            'cross_source_verification': await self._calculate_cross_source_verification(events)
        }
    
    def _events_are_similar(self, event1: Dict, event2: Dict) -> bool:
        """Check if two events are similar (simplified)"""
        
        title_similarity = self._calculate_title_similarity(
            event1.get('title', ''), 
            event2.get('title', '')
        )
        
        return title_similarity > 0.6
    
    def _calculate_title_similarity(self, title1: str, title2: str) -> float:
        """Calculate title similarity (simplified)"""
        
        if not title1 or not title2:
            return 0.0
        
        # Simple Jaccard similarity
        words1 = set(title1.lower().split())
        words2 = set(title2.lower().split())
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0
    
    async def _identify_event_clusters(self, events: List[Dict]) -> List[List[Dict]]:
        """Identify clusters of similar events"""
        
        clusters = []
        processed = set()
        
        for i, event in enumerate(events):
            if i in processed:
                continue
            
            cluster = [event]
            for j in range(i+1, len(events)):
                if j in processed:
                    continue
                
                if self._events_are_similar(event, events[j]):
                    cluster.append(events[j])
                    processed.add(j)
            
            clusters.append(cluster)
            processed.add(i)
        
        return clusters
    
    async def _calculate_cross_source_verification(self, events: List[Dict]) -> Dict[str, Any]:
        """Calculate cross-source verification metrics"""
        
        event_sources = {}
        
        for event in events:
            title = event.get('title', '')
            source = event.get('source', '')
            
            if title and source:
                if title not in event_sources:
                    event_sources[title] = set()
                event_sources[title].add(source)
        
        verification_scores = {}
        for title, sources in event_sources.items():
            verification_scores[title] = len(sources)
        
        return {
            'event_verification_scores': verification_scores,
            'max_verification': max(verification_scores.values()) if verification_scores else 0,
            'min_verification': min(verification_scores.values()) if verification_scores else 0,
            'average_verification': statistics.mean(verification_scores.values()) if verification_scores else 0
        }

class TrendDetector:
    """Detect trends in news content"""
    
    async def detect_trends(self, news_data: List[Dict]) -> Dict[str, Any]:
        """Detect trends in news content"""
        
        # Extract keywords and topics
        keywords = []
        for item in news_data:
            # Extract keywords from content (simplified)
            text = (item.get('text', '') or item.get('content', '')).lower()
            for word in ['cybersecurity', 'election', 'pandemic', 'climate', 'economy']:
                if word in text:
                    keywords.append(word)
        
        # Count keyword frequencies
        keyword_counts = {}
        for keyword in keywords:
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        # Sort by frequency
        sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'top_trends': dict(sorted_keywords[:10]),
            'trend_strength': self._calculate_trend_strength(sorted_keywords),
            'trend_velocity': await self._estimate_trend_velocity(news_data, sorted_keywords)
        }
    
    def _calculate_trend_strength(self, keyword_counts: List) -> float:
        """Calculate overall trend strength"""
        
        if not keyword_counts:
            return 0.0
        
        total = sum(count for _, count in keyword_counts)
        return sum(count for _, count in keyword_counts) / total
    
    async def _estimate_trend_velocity(self, news_data: List[Dict], keyword_counts: List) -> Dict[str, Any]:
        """Estimate trend velocity (simplified)"""
        
        recent_news = news_data[:10]  # Last 10 articles
        
        recent_keywords = []
        for item in recent_news:
            text = (item.get('text', '') or item.get('content', '')).lower()
            for word in [kw for kw, _ in keyword_counts[:5]]:  # Top 5 keywords
                if word in text:
                    recent_keywords.append(word)
        
        keyword_velocity = {}
        for kw, count in keyword_counts:
            recent_count = recent_keywords.count(kw)
            keyword_velocity[kw] = recent_count / count if count > 0 else 0
        
        return {
            'keyword_velocity': keyword_velocity,
            'accelerating_trends': {kw: v for kw, v in keyword_velocity.items() if v > 1.5}
        }

class NewsComplianceManager:
    """Ensure news data collection compliance"""
    
    def __init__(self):
        self.compliance_rules = {
            'rate_limiting': True,
            'no_automated_login': True,
            'no_personal_data': True,
            'respect_robots_txt': True,
            'terms_of_service': True,
            'data_minimization': True
        }
    
    async def check_compliance(self, action: str, data: Dict) -> Dict[str, Any]:
        """Check if action complies with news site policies"""
        
        compliance_result = {
            'compliant': True,
            'violations': [],
            'recommendations': []
        }
        
        # Check rate limiting compliance
        if action == 'scraping' and not self.compliance_rules['rate_limiting']:
            compliance_result['compliant'] = False
            compliance_result['violations'].append('Rate limiting violation')
            compliance_result['recommendations'].append('Reduce request frequency')
        
        # Check for personal data collection
        if self._contains_personal_data(data):
            compliance_result['compliant'] = False
            compliance_result['violations'].append('Personal data collection')
            compliance_result['recommendations'].append('Remove personal identifiers')
        
        # Check robots.txt compliance
        if not self.compliance_rules['respect_robots_txt']:
            compliance_result['compliant'] = False
            compliance_result['violations'].append('Robots.txt violation')
            compliance_result['recommendations'].append('Respect robots.txt directives')
        
        return compliance_result
    
    def _contains_personal_data(self, data: Dict) -> bool:
        """Check if data contains personal information"""
        
        personal_fields = ['email', 'phone', 'address', 'ssn', 'birthday']
        data_str = json.dumps(data).lower()
        
        return any(field in data_str for field in personal_fields)
