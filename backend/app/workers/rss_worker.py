import feedparser
import asyncio
from app.workers.scraper_base import BaseScraper
from app.streaming.kafka_producer import kafka_producer

class RSSScraper(BaseScraper):
    def __init__(self, feed_url: str):
        super().__init__(name="RSS_Scraper")
        self.feed_url = feed_url

    async def scrape(self):
        print(f"Scraping RSS: {self.feed_url}")
        feed = feedparser.parse(self.feed_url)
        
        for entry in feed.entries:
            signal_data = {
                "source_type": "news",
                "source_name": self.name,
                "title": entry.get("title", ""),
                "content": entry.get("summary", ""),
                "url": entry.get("link", ""),
                "published": entry.get("published", "")
            }
            # Send to Kafka for processing
            await kafka_producer.send_signal("raw_signals", signal_data)
        
        return len(feed.entries)

# Example usage in a worker loop
async def run_rss_ingestion(url: str):
    scraper = RSSScraper(url)
    while True:
        count = await scraper.scrape()
        print(f"Ingested {count} signals from {url}")
        await asyncio.sleep(600)  # Sleep 10 mins
