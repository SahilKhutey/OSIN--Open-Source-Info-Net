#!/usr/bin/env python3
"""
OSIN Geo-Tagging Pipeline Integration
Connects entity extraction to geotagging service
"""

import json
import requests
import logging
import time
import os
import signal
import sys
from kafka import KafkaConsumer, KafkaProducer
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("osin-geotagging-integration")

# Configuration via environment variables
GEOTAGGING_SERVICE = os.getenv("GEOTAGGING_SERVICE", "http://osin-geotagging:8004/geotag")
KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "localhost:9092,kafka-broker:9092").split(",")
INPUT_TOPIC = os.getenv("INPUT_TOPIC", "osin-deduplicated")
OUTPUT_TOPIC = os.getenv("OUTPUT_TOPIC", "osin-geotagged")
ERROR_TOPIC = os.getenv("ERROR_TOPIC", "osin-geotagging-errors")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "50"))

class GeotaggingIntegrator:
    def __init__(self):
        self.running = True
        self.setup_signal_handlers()
    
    def setup_signal_handlers(self):
        """Setup graceful shutdown handlers"""
        signal.signal(signal.SIGINT, self.graceful_shutdown)
        signal.signal(signal.SIGTERM, self.graceful_shutdown)
    
    def graceful_shutdown(self, signum, frame):
        """Handle graceful shutdown"""
        logger.info(f"Received shutdown signal ({signum}), stopping...")
        self.running = False
    
    def create_kafka_clients(self):
        """Create Kafka consumer and producer"""
        try:
            consumer = KafkaConsumer(
                INPUT_TOPIC,
                bootstrap_servers=KAFKA_BROKERS,
                group_id="osin-geotagging-group",
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                auto_offset_reset='latest',
                enable_auto_commit=True,
                auto_commit_interval_ms=5000
            )
            
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKERS,
                value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                acks='all',
                retries=3,
                compression_type='gzip'
            )
            
            return consumer, producer
            
        except Exception as e:
            logger.error(f"Kafka client creation failed: {e}")
            raise
    
    def geotag_event(self, event: Dict) -> Dict:
        """Add geographic coordinates to event via Geo-Tagging Service"""
        # Skip if already geotagged
        if event.get('lat') and event.get('lon'):
            return event
            
        try:
            geotag_request = {
                "text": event.get('text') or event.get('content', ''),
                "event_id": event.get('id'),
                "source": event.get('source', 'unknown'),
                "confidence": event.get('confidence', 0.5)
            }
            
            response = requests.post(
                GEOTAGGING_SERVICE,
                json=geotag_request,
                timeout=20
            )
            response.raise_for_status()
            
            geotag_data = response.json()
            
            # Enrich original event with coordinates
            if geotag_data.get('locations'):
                # Use the primary (first) location detected
                primary = geotag_data['locations'][0]
                event['lat'] = primary['lat']
                event['lon'] = primary['lon']
                event['location_name'] = primary['location']
                event['geotag_confidence'] = primary['confidence']
                event['geotag_source'] = primary['source']
                
                # Boost confidence based on spatial grounding
                event['confidence'] = min(1.0, event.get('confidence', 0.5) + 0.1)
                event['geotagging_status'] = 'success'
                
                logger.info(f"Geotagged event {event.get('id')}: {primary['location']}")
            else:
                event['geotagging_status'] = 'no_location_found'
                logger.debug(f"No locations found for event {event.get('id')}")
            
            return event
            
        except Exception as e:
            logger.error(f"Geotagging failed for event {event.get('id')}: {e}")
            event['geotagging_error'] = str(e)
            return event
    
    def run(self):
        """Main processing loop"""
        logger.info("Starting OSIN Geo-Tagging Integration Service v2.1.0")
        
        try:
            consumer, producer = self.create_kafka_clients()
            logger.info("Kafka clients initialized successfully")
            
            while self.running:
                try:
                    # Poll for messages
                    messages = consumer.poll(timeout_ms=1000, max_records=BATCH_SIZE)
                    
                    if not messages:
                        continue
                        
                    for topic_partition, msg_list in messages.items():
                        for message in msg_list:
                            if not self.running:
                                break
                            
                            event = message.value
                            if event:
                                # Geotag the event signal
                                geotagged_event = self.geotag_event(event)
                                
                                # Send to output topic for Geo-Intelligence verification
                                producer.send(OUTPUT_TOPIC, geotagged_event)
                                logger.debug(f"Processed event: {geotagged_event.get('id')}")
                    
                    # Manual flush
                    producer.flush()
                    
                except Exception as e:
                    logger.error(f"Error in processing loop: {e}")
                    time.sleep(1)
        
        except Exception as e:
            logger.critical(f"Fatal error in Geotagging Integrator: {e}")
            sys.exit(1)
        
        finally:
            logger.info("Geo-tagging integration stopped")

if __name__ == "__main__":
    integrator = GeotaggingIntegrator()
    integrator.run()
