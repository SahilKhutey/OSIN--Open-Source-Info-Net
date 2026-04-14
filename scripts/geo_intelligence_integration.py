#!/usr/bin/env python3
"""
OSIN Geo-Intelligence Pipeline Integration - v2.1.0 (Enhanced)
Connects deduplication to enhanced geo-intelligence enrichment
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
logger = logging.getLogger("osin-geo-intelligence-integration")

# Configuration via environment variables
GEO_SERVICE = os.getenv("GEO_SERVICE", "http://osin-geo-intelligence:8003/geo-intel")
KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "localhost:9092,kafka-broker:9092").split(",")
INPUT_TOPIC = os.getenv("INPUT_TOPIC", "osin-deduplicated")
OUTPUT_TOPIC = os.getenv("OUTPUT_TOPIC", "osin-enriched")
ERROR_TOPIC = os.getenv("ERROR_TOPIC", "osin-geo-intel-errors")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "50"))

class GeoIntelligenceIntegrator:
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
                group_id="osin-geo-intel-group",
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
    
    def enrich_with_geo_intel(self, event: Dict) -> Dict:
        """Enrich event with NASA geo-intelligence data using enhanced logic"""
        # Data Extraction
        lat = event.get('lat') or (event.get('location', {}).get('lat') if isinstance(event.get('location'), dict) else None)
        lon = event.get('lon') or (event.get('location', {}).get('lng') if isinstance(event.get('location'), dict) else None)
        
        if lat is None or lon is None:
            logger.debug(f"Event {event.get('id')} missing coordinates, skipping geo-intel")
            return event
        
        try:
            # Enrichment Request
            enrichment_request = {
                "event_id": event.get('id', 'unknown'),
                "text": event.get('text') or event.get('content', ''),
                "lat": float(lat),
                "lon": float(lon),
                "timestamp": event.get('timestamp') or time.time(),
                "source": event.get('source', 'unknown'),
                "entities": event.get('entities'),
                "confidence": event.get('confidence', 0.5),
                "event_type": event.get('event_type') # Pass event_type for better layer selection
            }
            
            response = requests.post(
                GEO_SERVICE,
                json=enrichment_request,
                timeout=30
            )
            response.raise_for_status()
            
            geo_data = response.json()
            
            # Merge enhanced geo-intel data with original event
            event['geo_intel'] = geo_data
            event['confidence'] = geo_data.get('confidence_impact', event.get('confidence', 0.5))
            event['verification_status'] = 'geo_verified'
            
            logger.info(f"Enriched event {event.get('id')} with enhanced geo-intelligence")
            return event
            
        except Exception as e:
            logger.error(f"Geo-intel enrichment failed for event {event.get('id')}: {e}")
            event['geo_intel_error'] = str(e)
            return event
    
    def run(self):
        """Main processing loop"""
        logger.info("Starting OSIN Geo-Intelligence Integration Service v2.1.0-enhanced")
        
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
                                # Process through enhanced enrichment
                                enriched_event = self.enrich_with_geo_intel(event)
                                
                                # Send to output topic
                                producer.send(OUTPUT_TOPIC, enriched_event)
                    
                    # Periodic flush
                    producer.flush()
                    
                except Exception as e:
                    logger.error(f"Error in processing loop: {e}")
                    time.sleep(1)
        
        except Exception as e:
            logger.critical(f"Fatal error in Geo Integrator: {e}")
            sys.exit(1)
        
        finally:
            logger.info("Geo-intelligence integration stopped")

if __name__ == "__main__":
    integrator = GeoIntelligenceIntegrator()
    integrator.run()
