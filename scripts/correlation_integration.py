#!/usr/bin/env python3
"""
OSIN Graph Correlation Integration
Connects enriched signals to the Cross-Platform Correlation Engine
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
logger = logging.getLogger("osin-correlation-integration")

# Configuration via environment variables
CORRELATION_SERVICE = os.getenv("CORRELATION_SERVICE", "http://osin-correlation:8005/correlate")
KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "localhost:9092,kafka-broker:9092").split(",")
INPUT_TOPIC = os.getenv("INPUT_TOPIC", "osin-enriched") # Signals that have been deduplicated, geotagged, and geo-intel verified
OUTPUT_TOPIC = os.getenv("OUTPUT_TOPIC", "osin-correlated") # Final stage output

class CorrelationIntegrator:
    def __init__(self):
        self.running = True
        self.setup_signal_handlers()
    
    def setup_signal_handlers(self):
        signal.signal(signal.SIGINT, self.graceful_shutdown)
        signal.signal(signal.SIGTERM, self.graceful_shutdown)
    
    def graceful_shutdown(self, signum, frame):
        logger.info(f"Shutting down correlation integration ({signum})...")
        self.running = False
    
    def create_kafka_clients(self):
        try:
            consumer = KafkaConsumer(
                INPUT_TOPIC,
                bootstrap_servers=KAFKA_BROKERS,
                group_id="osin-correlation-group",
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                auto_offset_reset='latest'
            )
            
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKERS,
                value_serializer=lambda x: json.dumps(x).encode('utf-8')
            )
            
            return consumer, producer
        except Exception as e:
            logger.error(f"Kafka connection failed: {e}")
            raise
    
    def process_correlation(self, event: Dict) -> Dict:
        """Send signal to Correlation Engine for graph linking"""
        try:
            # Map event entities to Correlation Service format
            raw_entities = event.get('entities', [])
            formatted_entities = []
            
            # Extract hashtags as entities
            if 'hashtags' in event:
                for ht in event['hashtags']:
                    formatted_entities.append({"name": ht, "type": "HASHTAG"})
            
            # Map other entities if available
            if isinstance(raw_entities, list):
                for ent in raw_entities:
                    if isinstance(ent, dict):
                        formatted_entities.append({
                            "name": ent.get('name', ent.get('text', '')),
                            "type": ent.get('type', 'GENERIC')
                        })
            
            correlation_request = {
                "event_id": event.get('id'),
                "text": event.get('text') or event.get('content', ''),
                "lat": event.get('lat'),
                "lon": event.get('lon'),
                "entities": formatted_entities,
                "timestamp": event.get('timestamp') or time.time(),
                "source": event.get('source', 'unknown'),
                "confidence": event.get('confidence', 0.5)
            }
            
            response = requests.post(CORRELATION_SERVICE, json=correlation_request, timeout=10)
            response.raise_for_status()
            
            correlation_data = response.json()
            event['correlation_metadata'] = correlation_data
            event['correlated_signals_count'] = len(correlation_data.get('correlated_ids', []))
            
            logger.info(f"Associated signal {event.get('id')} with {event['correlated_signals_count']} existing signals")
            
            return event
            
        except Exception as e:
            logger.error(f"Correlation failed for {event.get('id')}: {e}")
            event['correlation_error'] = str(e)
            return event
    
    def run(self):
        logger.info("Starting OSIN Graph Correlation Integrator v2.2.0")
        
        try:
            consumer, producer = self.create_kafka_clients()
            
            for message in consumer:
                if not self.running: break
                
                event = message.value
                if event:
                    correlated_event = self.process_correlation(event)
                    producer.send(OUTPUT_TOPIC, correlated_event)
                    
            producer.flush()
        except Exception as e:
            logger.critical(f"Fatal error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    integrator = CorrelationIntegrator()
    integrator.run()
