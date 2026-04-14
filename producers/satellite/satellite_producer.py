import os
import time
import json
import requests
import logging
from datetime import datetime
from server.lib.tracing.trace_manager import traced
from server.lib.producers.enhanced_producer import EnhancedProducer
from server.lib.backpressure.backpressure_manager import BackpressureManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SatelliteProducer")

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")
TOPIC_NAME = "osin.raw.satellite"
NASA_EONET_URL = "https://eonet.gsfc.nasa.gov/api/v3/events"
SERVICE_NAME = "satellite-producer"

@traced(SERVICE_NAME, "fetch_satellite_events")
def fetch_satellite_events():
    """Fetches real-time natural events from NASA EONET"""
    try:
        response = requests.get(NASA_EONET_URL, params={"status": "open"}, timeout=10)
        if response.status_code == 200:
            events = response.json().get('events', [])
            logger.info(f"Fetched {len(events)} satellite events from NASA")
            return events
        else:
            logger.error(f"NASA API Error: {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"Error fetching NASA data: {e}")
        return []

def main():
    # Initialize SVP-2 Enhanced Components
    producer = EnhancedProducer(KAFKA_BOOTSTRAP_SERVERS, SERVICE_NAME)
    backpressure = BackpressureManager(service_name=SERVICE_NAME)
    
    logger.info(f"OSIN {SERVICE_NAME} Started with SVP-2 Enhancements")
    
    last_event_ids = set()
    
    while True:
        # Check for system backpressure before processing
        backpressure.check_and_throttle()
        
        events = fetch_satellite_events()
        
        for event in events:
            event_id = event.get('id')
            if event_id not in last_event_ids:
                # Construct Intelligence Payload
                payload = {
                    "source": "NASA_EONET",
                    "id": event_id,
                    "title": event.get('title'),
                    "category": event.get('categories', [{}])[0].get('title'),
                    "timestamp": datetime.utcnow().isoformat(),
                    "coordinates": event.get('geometries', [{}])[0].get('coordinates'),
                    "raw_data": event
                }
                
                # Use Traced Sending
                producer.send_traced(TOPIC_NAME, payload, key=event_id)
                logger.info(f"Ingested Satellite Event: {event_id} - {payload['title']}")
                last_event_ids.add(event_id)
        
        # Maintain Sliding Window
        if len(last_event_ids) > 1000:
            last_event_ids = set(list(last_event_ids)[-500:])
            
        # Poll interval (10 minutes)
        time.sleep(600)

if __name__ == "__main__":
    main()
