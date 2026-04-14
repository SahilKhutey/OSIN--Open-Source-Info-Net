#!/usr/bin/env python3
"""
OSIN Mapillary Pipeline Integration
Connects enriched events to street-level intelligence
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
logger = logging.getLogger("osin-mapillary-integration")

# Configuration via environment variables
MAPILLARY_SERVICE = os.getenv("MAPILLARY_SERVICE", "http://osin-mapillary:8006/street-intel")
KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "localhost:9092,kafka-broker:9092").split(",")
INPUT_TOPIC = os.getenv("INPUT_TOPIC", "osin-arcgis-enriched")
OUTPUT_TOPIC = os.getenv("OUTPUT_TOPIC", "osin-street-enriched")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "50"))

class MapillaryIntegrator:
    def __init__(self):
        self.running = True
        self.setup_signal_handlers()
    
    def setup_signal_handlers(self):
        signal.signal(signal.SIGINT, self.graceful_shutdown)
        signal.signal(signal.SIGTERM, self.graceful_shutdown)
    
    def graceful_shutdown(self, signum, frame):
        logger.info(f"Shutting down Mapillary integration ({signum})...")
        self.running = False
    
    def create_kafka_clients(self):
        try:
            consumer = KafkaConsumer(
                INPUT_TOPIC,
                bootstrap_servers=KAFKA_BROKERS,
                group_id="osin-mapillary-group",
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                auto_offset_reset='latest',
                enable_auto_commit=True
            )
            
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKERS,
                value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                acks='all'
            )
            
            return consumer, producer
        except Exception as e:
            logger.error(f"Kafka connection failed: {e}")
            raise
    
    def enrich_with_street_intel(self, event: Dict) -> Dict:
        """Enrich event with street-level imagery intelligence"""
        if not event.get('lat') or not event.get('lon'):
            logger.debug(f"Event {event.get('id')} missing coordinates, skipping street-intel")
            return event
            
        try:
            enrich_req = {
                "event_id": event.get('id'),
                "lat": float(event['lat']),
                "lon": float(event['lon']),
                "text": event.get('text') or event.get('content', ''),
                "event_type": event.get('event_type') or event.get('type'),
                "confidence": event.get('confidence', 0.5),
                "timestamp": event.get('timestamp') or time.time()
            }
            
            response = requests.post(MAPILLARY_SERVICE, json=enrich_req, timeout=30)
            response.raise_for_status()
            
            street_data = response.json()
            
            # Merge street view intelligence
            event['street_intel'] = street_data
            event['confidence'] = street_data.get('confidence_impact', event.get('confidence', 0.5))
            
            # Final verification status
            if street_data.get('images_found', 0) > 0:
                event['verification_status'] = 'street_verified'
                logger.info(f"Signal {event.get('id')} street-verified with {street_data['images_found']} images")
            else:
                event['verification_status'] = 'no_street_coverage'
                
            return event
            
        except Exception as e:
            logger.error(f"Street-intel enrichment failed for {event.get('id')}: {e}")
            event['street_error'] = str(e)
            return event
    
    def run(self):
        logger.info("Starting OSIN Mapillary Integration Service v2.4.0")
        
        try:
            consumer, producer = self.create_kafka_clients()
            
            while self.running:
                messages = consumer.poll(timeout_ms=1000, max_records=BATCH_SIZE)
                if not messages: continue
                
                for tp, msg_list in messages.items():
                    for message in msg_list:
                        if not self.running: break
                        
                        event = message.value
                        if event:
                            enriched_event = self.enrich_with_street_intel(event)
                            producer.send(OUTPUT_TOPIC, enriched_event)
                
                producer.flush()
                
        except Exception as e:
            logger.critical(f"Fatal error in Mapillary Integrator: {e}")
            sys.exit(1)
        finally:
            logger.info("Mapillary integration stopped")

if __name__ == "__main__":
    integrator = MapillaryIntegrator()
    integrator.run()
