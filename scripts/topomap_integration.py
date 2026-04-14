#!/usr/bin/env python3
"""
OSIN TopoMap Pipeline Integration
Connects weather-enriched events to topographic intelligence
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
logger = logging.getLogger("osin-topomap-integration")

# Configuration via environment variables
TOPOMAP_SERVICE = os.getenv("TOPOMAP_SERVICE", "http://osin-topomap:8008/topo-intel")
KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "localhost:9092,kafka-broker:9092").split(",")
INPUT_TOPIC = os.getenv("INPUT_TOPIC", "osin-weather-enriched")
OUTPUT_TOPIC = os.getenv("OUTPUT_TOPIC", "osin-topo-enriched")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "50"))

class TopoMapIntegrator:
    def __init__(self):
        self.running = True
        self.setup_signal_handlers()
    
    def setup_signal_handlers(self):
        signal.signal(signal.SIGINT, self.graceful_shutdown)
        signal.signal(signal.SIGTERM, self.graceful_shutdown)
    
    def graceful_shutdown(self, signum, frame):
        logger.info(f"Shutting down TopoMap integration ({signum})...")
        self.running = False
    
    def create_kafka_clients(self):
        try:
            consumer = KafkaConsumer(
                INPUT_TOPIC,
                bootstrap_servers=KAFKA_BROKERS,
                group_id="osin-topomap-group",
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
    
    def enrich_event(self, event: Dict) -> Dict:
        """Enrich intelligence object with topographic and terrain analysis"""
        if not event.get('lat') or not event.get('lon'):
            return event
            
        try:
            enrich_req = {
                "event_id": event.get('id'),
                "lat": float(event['lat']),
                "lon": float(event['lon']),
                "text": event.get('text') or event.get('content', ''),
                "event_type": event.get('event_type'),
                "confidence": event.get('confidence', 0.5),
                "timestamp": event.get('timestamp') or time.time()
            }
            
            response = requests.post(TOPOMAP_SERVICE, json=enrich_req, timeout=30)
            response.raise_for_status()
            
            topo_data = response.json()
            
            # Merge terrain intelligence into the fused object
            event['topo_intel'] = topo_data
            event['confidence'] = topo_data.get('confidence_impact', event.get('confidence', 0.5))
            
            # Final status update for the end-to-end chain
            event['verification_status'] = 'fully_fused_v2.6'
            event['last_fusion_layer'] = 'topography'
            
            logger.info(f"Fused terrain intelligence for event {event.get('id')}")
            return event
            
        except Exception as e:
            logger.error(f"Topo enrichment failed for {event.get('id')}: {e}")
            event['topo_error'] = str(e)
            return event
    
    def run(self):
        logger.info("Starting OSIN TopoMap Integration Service v2.6.0")
        
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
                            enriched_event = self.enrich_event(event)
                            producer.send(OUTPUT_TOPIC, enriched_event)
                
                producer.flush()
                
        except Exception as e:
            logger.critical(f"Fatal error in TopoMap Integrator: {e}")
            sys.exit(1)
        finally:
            logger.info("TopoMap integration stopped")

if __name__ == "__main__":
    integrator = TopoMapIntegrator()
    integrator.run()
