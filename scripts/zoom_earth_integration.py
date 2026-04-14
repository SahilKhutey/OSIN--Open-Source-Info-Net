#!/usr/bin/env python3
"""
OSIN Zoom Earth Pipeline Integration
Connects street-enriched events to weather intelligence
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
logger = logging.getLogger("osin-zoom-earth-integration")

# Configuration via environment variables
WEATHER_SERVICE = os.getenv("WEATHER_SERVICE", "http://osin-zoom-earth:8007/weather-intel")
KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "localhost:9092,kafka-broker:9092").split(",")
INPUT_TOPIC = os.getenv("INPUT_TOPIC", "osin-street-enriched")
OUTPUT_TOPIC = os.getenv("OUTPUT_TOPIC", "osin-weather-enriched")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "50"))

class ZoomEarthIntegrator:
    def __init__(self):
        self.running = True
        self.setup_signal_handlers()
    
    def setup_signal_handlers(self):
        signal.signal(signal.SIGINT, self.graceful_shutdown)
        signal.signal(signal.SIGTERM, self.graceful_shutdown)
    
    def graceful_shutdown(self, signum, frame):
        logger.info(f"Shutting down Weather integration ({signum})...")
        self.running = False
    
    def create_kafka_clients(self):
        try:
            consumer = KafkaConsumer(
                INPUT_TOPIC,
                bootstrap_servers=KAFKA_BROKERS,
                group_id="osin-weather-group",
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
        """Enrich intelligence object with live weather context"""
        if not event.get('lat') or not event.get('lon'):
            logger.debug(f"Event {event.get('id')} missing coordinates, skipping weather enrichment")
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
            
            response = requests.post(WEATHER_SERVICE, json=enrich_req, timeout=30)
            response.raise_for_status()
            
            weather_data = response.json()
            
            # Merge weather analytics into the intelligence object
            event['weather_intel'] = weather_data
            event['confidence'] = weather_data.get('confidence_impact', event.get('confidence', 0.5))
            
            total_alerts = len(weather_data.get('severe_alerts', []))
            if total_alerts > 0:
                event['verification_status'] = 'weather_alert_verified'
                logger.info(f"Weather alert verification for event {event.get('id')}: {total_alerts} alerts")
            else:
                event['verification_status'] = 'weather_context_added'
            
            return event
            
        except Exception as e:
            logger.error(f"Weather enrichment failed for {event.get('id')}: {e}")
            event['weather_error'] = str(e)
            return event
    
    def run(self):
        logger.info("Starting OSIN Zoom Earth Integration Service v2.5.0")
        
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
            logger.critical(f"Fatal error in Weather Integrator: {e}")
            sys.exit(1)
        finally:
            logger.info("Weather integration stopped")

if __name__ == "__main__":
    integrator = ZoomEarthIntegrator()
    integrator.run()
