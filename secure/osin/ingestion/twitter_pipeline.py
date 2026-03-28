import snscrape.modules.twitter as sntwitter
from kafka import KafkaProducer
import json
import time
import asyncio
from datetime import datetime, timedelta
import logging
from typing import Generator, Dict, Any
from architecture import IngestionConfig
from shared_components import RateLimiter, DeduplicationEngine, ContentCleaner
from monitoring import monitor
import time

class TwitterIngestionEngine:
    """High-performance Twitter data ingestion"""
    
    def __init__(self, config: IngestionConfig):
        self.config = config
        self.producer = KafkaProducer(
            bootstrap_servers=config.kafka_brokers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            batch_size=config.batch_size,
            linger_ms=500,
            retries=config.retry_attempts
        )
        self.deduplicator = DeduplicationEngine()
        self.cleaner = ContentCleaner()
        self.rate_limiter = RateLimiter(config.rate_limit['twitter'])
        
    def generate_search_queries(self) -> List[str]:
        """Generate comprehensive search queries"""
        
        base_queries = [
            # Breaking news and events
            "breaking news", "emergency", "crisis", "disaster",
            # Global events
            "protest", "election", "summit", "conference",
            # Trending topics
            "trending", "viral", "hot topic",
            # Specific event types
            "earthquake", "fire", "flood", "storm",
            # Political events
            "election results", "political", "government",
            # Economic events
            "stock market", "economy", "trade",
            # Technology events
            "cyber attack", "data breach", "tech news"
        ]
        
        # Add location-specific queries
        locations = ["USA", "Europe", "Asia", "Middle East", "Africa", "Latin America"]
        enhanced_queries = []
        
        for query in base_queries:
            for location in locations:
                enhanced_queries.append(f"{query} {location}")
            enhanced_queries.append(query)  # Keep original
        
        return enhanced_queries
    
    async def stream_tweets(self) -> Generator[Dict[str, Any], None, None]:
        """Stream tweets using multiple search strategies"""
        
        queries = self.generate_search_queries()
        
        for query in queries:
            if not self.rate_limiter.can_proceed():
                await asyncio.sleep(60)
                continue
            
            try:
                scraper = sntwitter.TwitterSearchScraper(query)
                
                for i, tweet in enumerate(scraper.get_items()):
                    if i >= 1000:  # Limit per query
                        break
                    
                    if not self.rate_limiter.can_proceed():
                        await asyncio.sleep(60)
                        continue
                    
                    start_time = time.time()
                    tweet_data = self._process_tweet(tweet)
                    tweet_data = self.cleaner.clean_content(tweet_data)
                    
                    # Deduplication check
                    if not self.deduplicator.is_duplicate(tweet_data):
                        self.rate_limiter.record_request()
                        latency = time.time() - start_time
                        monitor.record_request('twitter', 'success', latency)
                        monitor.record_content_volume('twitter', 'tweet', 1)
                        yield tweet_data
                
            except Exception as e:
                logging.error(f"Twitter scraping error for query '{query}': {e}")
                continue
    
    def _process_tweet(self, tweet) -> Dict[str, Any]:
        """Process raw tweet into standardized format"""
        
        return {
            "platform": "twitter",
            "id": str(tweet.id),
            "text": tweet.rawContent,
            "user": {
                "id": str(tweet.user.id),
                "username": tweet.user.username,
                "display_name": tweet.user.displayname,
                "verified": tweet.user.verified,
                "followers": tweet.user.followersCount,
                "following": tweet.user.friendsCount
            },
            "engagement": {
                "likes": tweet.likeCount,
                "retweets": tweet.retweetCount,
                "replies": tweet.replyCount,
                "quotes": tweet.quoteCount
            },
            "metadata": {
                "timestamp": tweet.date.isoformat(),
                "language": tweet.lang,
                "has_media": tweet.media is not None,
                "has_links": tweet.outlinks is not None,
                "source": str(tweet.source),
                "coordinates": getattr(tweet, 'coordinates', None)
            },
            "raw_data": {
                "url": tweet.url,
                "conversation_id": str(tweet.conversationId),
                "retweeted_tweet": str(tweet.retweetedTweet.id) if tweet.retweetedTweet else None,
                "quoted_tweet": str(tweet.quotedTweet.id) if tweet.quotedTweet else None
            },
            "processing_metadata": {
                "collected_at": datetime.utcnow().isoformat(),
                "query_used": getattr(tweet, '_query', 'unknown'),
                "processing_version": "2.0"
            }
        }
    
    async def start_streaming(self):
        """Start continuous tweet streaming"""
        
        logging.info("Starting Twitter ingestion engine")
        
        while True:
            try:
                async for tweet in self.stream_tweets():
                    # Send to Kafka
                    self.producer.send("raw.twitter.posts", tweet)
                    
                    # Flush periodically
                    if datetime.utcnow().second % self.config.flush_interval == 0:
                        self.producer.flush()
                
                # Brief pause between query cycles
                await asyncio.sleep(10)
                
            except Exception as e:
                logging.error(f"Twitter streaming error: {e}")
                await asyncio.sleep(60)  # Backoff on error

if __name__ == "__main__":
    monitor.start_metrics_server(port=8000)
    config = IngestionConfig()
    engine = TwitterIngestionEngine(config)
    
    # Start asynchronous streaming
    asyncio.run(engine.start_streaming())
