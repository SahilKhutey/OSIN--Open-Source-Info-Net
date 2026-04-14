import os
import time
import json
import logging
import random
from datetime import datetime
import tweepy
from server.lib.tracing.trace_manager import traced
from server.lib.producers.enhanced_producer import EnhancedProducer
from server.lib.backpressure.backpressure_manager import BackpressureManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SocialProducer")

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")
TOPIC_NAME = "osin.raw.social"
SERVICE_NAME = "social-producer"
OSINT_TAGS = ["#breaking", "#breakingnews", "#cybersecurity", "#geopolitics", "#earthquake", "#threatintel"]

class OSINTStreamListener(tweepy.StreamingClient):
    def __init__(self, bearer_token, producer: EnhancedProducer, backpressure: BackpressureManager):
        super().__init__(bearer_token)
        self.producer = producer
        self.backpressure = backpressure

    def on_tweet(self, tweet):
        try:
            # Check backpressure before ingesting
            self.backpressure.check_and_throttle()
            
            payload = {
                "source": "Twitter_OSINT",
                "id": str(tweet.id),
                "text": tweet.text,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {
                    "author_id": str(tweet.author_id),
                    "edit_history": tweet.edit_history_tweet_ids
                }
            }
            
            # SVP-2 Traced Sending
            self.producer.send_traced(TOPIC_NAME, payload, key=str(tweet.id))
            logger.info(f"Ingested OSINT Tweet: {tweet.id}")
        except Exception as e:
            logger.error(f"Error processing tweet: {e}")

def main():
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    producer = EnhancedProducer(KAFKA_BOOTSTRAP_SERVERS, SERVICE_NAME)
    backpressure = BackpressureManager(service_name=SERVICE_NAME)
    
    if not bearer_token or bearer_token == "REPLACE_ME":
        logger.warning("TWITTER_BEARER_TOKEN not set. Running in SVP-2 MOCK mode.")
        run_mock_stream(producer, backpressure)
        return

    stream = OSINTStreamListener(bearer_token, producer, backpressure)
    
    # Add rules for OSINT monitoring
    for tag in OSINT_TAGS:
        stream.add_rules(tweepy.StreamRule(tag))
    
    logger.info(f"OSIN {SERVICE_NAME} (Live) Started with SVP-2 Enhancements")
    stream.filter(tweet_fields=['author_id', 'created_at', 'text'])

@traced(SERVICE_NAME, "mock_social_stream")
def run_mock_stream(producer: EnhancedProducer, backpressure: BackpressureManager):
    """Fallback mock generator with SVP-2 protection if no API key is provided"""
    logger.info(f"OSIN {SERVICE_NAME} (Mock) Operational")
    
    mock_events = [
        "Intelligence: Surge in #geopolitics discussions detected in Zone Alpha.",
        "Breaking: Connectivity issues reported in Eastern Sector. #breakingnews",
        "Alert: Unusual data exfiltration pattern detected in #cybersecurity monitoring.",
        "Status: Tectonic activity update for #earthquake monitoring networks.",
    ]
    
    while True:
        # SVP-2 Backpressure Protection
        backpressure.check_and_throttle()
        
        event = random.choice(mock_events)
        payload = {
            "source": "Twitter_OSINT_Mock",
            "id": f"mock_{int(time.time()*1000)}",
            "text": event,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {"type": "simulated"}
        }
        
        # SVP-2 Traced Sending
        producer.send_traced(TOPIC_NAME, payload, key=payload['id'])
        logger.info(f"Ingested Mock Social Event: {payload['id']}")
        
        time.sleep(random.uniform(5, 15))

if __name__ == "__main__":
    main()
