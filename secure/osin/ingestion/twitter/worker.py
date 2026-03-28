# FILE: secure/osin/ingestion/twitter/worker.py
import snscrape.modules.twitter as sntwitter
from kafka import KafkaProducer
import json
import asyncio
import logging

class TwitterIngestionWorker:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=['kafka:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
    async def start_streaming(self):
        """Start Twitter streaming"""
        
        queries = [
            "breaking news", "emergency", "crisis", "disaster",
            "protest", "election", "summit", "trending"
        ]
        
        for query in queries:
            try:
                scraper = sntwitter.TwitterSearchScraper(query)
                
                for tweet in scraper.get_items():
                    if tweet is None:
                        continue
                    
                    processed = self.process_tweet(tweet)
                    self.producer.send('raw.twitter.posts', processed)
                    
                    # Rate limiting
                    await asyncio.sleep(0.1)
                    
            except Exception as e:
                logging.error(f"Twitter scraping error: {e}")
                continue
    
    def process_tweet(self, tweet):
        """Process tweet into standardized format"""
        
        return {
            'id': str(tweet.id),
            'text': tweet.rawContent,
            'user': tweet.user.username,
            'timestamp': tweet.date.isoformat(),
            'engagement': {
                'likes': tweet.likeCount,
                'retweets': tweet.retweetCount
            },
            'metadata': {
                'source': 'twitter',
                'language': tweet.lang,
                'has_media': tweet.media is not None
            }
        }

if __name__ == "__main__":
    worker = TwitterIngestionWorker()
    asyncio.run(worker.start_streaming())
