import feedparser
import requests
from kafka import KafkaProducer
import json
import asyncio
from datetime import datetime
import logging
from typing import List, Dict, Any
from architecture import IngestionConfig
from shared_components import DeduplicationEngine, ContentCleaner
from monitoring import monitor
from urllib.parse import urlparse
import hashlib
import time

class NewsIngestionEngine:
    """Global news aggregation from RSS feeds and APIs"""
    
    def __init__(self, config: IngestionConfig):
        self.config = config
        self.producer = KafkaProducer(
            bootstrap_servers=config.kafka_brokers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.rss_feeds = self._load_rss_feeds()
        self.news_apis = self._initialize_news_apis()
        self.deduplicator = DeduplicationEngine()
        self.cleaner = ContentCleaner()
        self.deduplicator = DeduplicationEngine()
        self.cleaner = ContentCleaner()
    
    def _load_rss_feeds(self) -> List[Dict[str, str]]:
        """Load comprehensive list of RSS feeds"""
        
        return [
            # International News
            {"name": "BBC World", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"},
            {"name": "Reuters World", "url": "https://www.reutersagency.com/feed/?best-topics=world-news&post_type=best"},
            {"name": "AP Top News", "url": "https://www.ap.org/rss/topnews.xml"},
            {"name": "Al Jazeera", "url": "https://www.aljazeera.com/xml/rss/all.xml"},
            
            # Regional News
            {"name": "CNN International", "url": "http://rss.cnn.com/rss/edition.rss"},
            {"name": "DW News", "url": "https://rss.dw.com/rdf/rss-en-all"},
            {"name": "France24", "url": "https://www.france24.com/en/rss"},
            
            # Specialized News
            {"name": "TechCrunch", "url": "https://techcrunch.com/feed/"},
            {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index"},
            {"name": "Bloomberg", "url": "https://www.bloomberg.com/feed/podcast/etf-report.xml"},
            
            # Government and Official Sources
            {"name": "UN News", "url": "https://news.un.org/feed/subscribe/en/news/all/rss.xml"},
            {"name": "US State Dept", "url": "https://www.state.gov/rss-feed/"},
        ]
    
    def _initialize_news_apis(self) -> List[Dict]:
        """Initialize news API clients"""
        
        return [
            {
                "name": "NewsAPI",
                "client": None,  # Would be API client
                "rate_limit": 1000
            },
            {
                "name": "GDELT",
                "client": None,
                "rate_limit": 10000
            }
        ]
    
    async def monitor_rss_feeds(self):
        """Monitor all RSS feeds continuously"""
        
        while True:
            for feed in self.rss_feeds:
                try:
                    start_time = time.time()
                    articles = await self._parse_rss_feed(feed)
                    for article in articles:
                        article = self.cleaner.clean_content(article)
                        if not self.deduplicator.is_duplicate(article):
                            self.producer.send("raw.news.articles", article)
                            latency = time.time() - start_time
                            monitor.record_request('news', 'success', latency)
                            monitor.record_content_volume('news', 'article', 1)
                    
                    await asyncio.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    logging.error(f"Error parsing RSS feed {feed['name']}: {e}")
                    continue
            
            # Wait before next cycle
            await asyncio.sleep(300)  # 5 minutes between cycles
    
    async def _parse_rss_feed(self, feed: Dict) -> List[Dict[str, Any]]:
        """Parse RSS feed and extract articles"""
        
        parsed_feed = feedparser.parse(feed['url'])
        articles = []
        
        for entry in parsed_feed.entries:
            article = self._process_rss_entry(entry, feed['name'])
            articles.append(article)
        
        return articles
    
    def _process_rss_entry(self, entry, source_name: str) -> Dict[str, Any]:
        """Process RSS entry into standardized format"""
        
        return {
            "platform": "news",
            "source": source_name,
            "id": entry.get('id', entry.link),
            "title": entry.title,
            "summary": entry.summary if hasattr(entry, 'summary') else '',
            "content": entry.content[0].value if hasattr(entry, 'content') else '',
            "author": entry.author if hasattr(entry, 'author') else '',
            "metadata": {
                "published": entry.published if hasattr(entry, 'published') else '',
                "updated": entry.updated if hasattr(entry, 'updated') else '',
                "link": entry.link,
                "language": getattr(entry, 'language', 'en')
            },
            "categorization": {
                "categories": entry.tags if hasattr(entry, 'tags') else [],
                "source_type": "rss"
            },
            "processing_metadata": {
                "collected_at": datetime.utcnow().isoformat(),
                "processing_version": "2.0"
            }
        }
    
    async def fetch_gdelt_events(self):
        """Fetch events from GDELT Project"""
        
        try:
            # GDELT 2.0 API endpoint
            url = "https://api.gdeltproject.org/api/v2/doc/doc"
            
            # Query for recent global events
            params = {
                'query': 'sourcelang:english',
                'mode': 'artlist',
                'maxrecords': 100,
                'format': 'json'
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                
                for article in data.get('articles', []):
                    gdelt_event = self._process_gdelt_article(article)
                    self.producer.send("raw.news.articles", gdelt_event)
        
        except Exception as e:
            logging.error(f"Error fetching GDELT data: {e}")
    
    def _process_gdelt_article(self, article: Dict) -> Dict[str, Any]:
        """Process GDELT article into standardized format"""
        
        return {
            "platform": "news",
            "source": "gdelt",
            "id": article['url'],
            "title": article['title'],
            "content": article['seendata'],
            "metadata": {
                "published": article['seendate'],
                "url": article['url'],
                "language": article['language'],
                "source_country": article.get('sourcecountry', '')
            },
            "gdelt_metadata": {
                "tone": article.get('tone', 0),
                "positive_score": article.get('positive', 0),
                "negative_score": article.get('negative', 0),
                "word_count": article.get('wordcount', 0)
            },
            "processing_metadata": {
                "collected_at": datetime.utcnow().isoformat(),
                "processing_version": "2.0"
            }
        }

class NewsDeduplicator:
    """Deduplicate news articles across sources"""
    
    def __init__(self):
        self.seen_articles = set()
        self.similarity_threshold = 0.8
    
    def is_duplicate(self, article: Dict) -> bool:
        """Check if article is a duplicate"""
        
        article_hash = self._generate_article_hash(article)
        
        if article_hash in self.seen_articles:
            return True
        
        self.seen_articles.add(article_hash)
        return False
    
    def _generate_article_hash(self, article: Dict) -> str:
        """Generate hash for article deduplication"""
        
        content = f"{article['title']}_{article['source']}"
        return hashlib.md5(content.encode()).hexdigest()

if __name__ == "__main__":
    monitor.start_metrics_server(port=8000)
    config = IngestionConfig()
    engine = NewsIngestionEngine(config)
    
    # Start news monitoring
    asyncio.run(engine.monitor_rss_feeds())
