#!/usr/bin/env python3
"""
OSIN Pic2Map Pipeline Integration
Processes raw images and integrates them into the intelligence fusion stream
"""

import json
import requests
import logging
import time
import os
import signal
import sys
import base64
from io import BytesIO
from kafka import KafkaConsumer, KafkaProducer
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("osin-pic2map-integration")

# Configuration
PIC2MAP_SERVICE = os.getenv("PIC2MAP_SERVICE", "http://osin-pic2map:8009/image-intel")
KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "localhost:9092,kafka-broker:9092").split(",")
INPUT_TOPIC = os.getenv("INPUT_TOPIC", "osin-raw-images")
OUTPUT_TOPIC = os.getenv("OUTPUT_TOPIC", "osin-raw-signals") # Push back to the start of the text chain if geolocated
ENRICHED_TOPIC = os.getenv("ENRICHED_TOPIC", "osin-image-enriched")

class Pic2MapIntegrator:
    def __init__(self):
        self.running = True
        self.setup_signal_handlers()
    
    def setup_signal_handlers(self):
        signal.signal(signal.SIGINT, self.graceful_shutdown)
        signal.signal(signal.SIGTERM, self.graceful_shutdown)
    
    def graceful_shutdown(self, signum, frame):
        logger.info(f"Shutting down Pic2Map integration ({signum})...")
        self.running = False
    
    def create_kafka_clients(self):
        try:
            consumer = KafkaConsumer(
                INPUT_TOPIC,
                bootstrap_servers=KAFKA_BROKERS,
                group_id="osin-pic2map-group",
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
            logger.error(f"Kafka client initialization failed: {e}")
            raise
    
    def process_image(self, message: Dict) -> Optional[Dict]:
        """Send image buffer to Pic2Map service for analysis"""
        try:
            if 'image_b64' not in message:
                logger.warning("Message missing 'image_b64' data")
                return None
                
            img_data = base64.b64decode(message['image_b64'])
            img_format = message.get('format', 'jpeg')
            
            files = {
                'file': (f"upload.{img_format}", BytesIO(img_data), f"image/{img_format}")
            }
            
            data = {
                'event_id': message.get('id'),
                'source': message.get('source', 'automated_sensor')
            }
            
            response = requests.post(PIC2MAP_SERVICE, files=files, data=data, timeout=45)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Visual analysis failed: {e}")
            return None
    
    def run(self):
        logger.info("Starting OSIN Pic2Map Integration Service v2.7.0")
        
        try:
            consumer, producer = self.create_kafka_clients()
            
            for message in consumer:
                if not self.running: break
                
                raw_msg = message.value
                analysis = self.process_image(raw_msg)
                
                if analysis:
                    # If geolocated, generate a new OSINT signal to start the full fusion chain
                    if analysis.get('gps_data'):
                        signal_msg = {
                            "id": analysis['event_id'],
                            "content": f"Visual Intelligence Report: {analysis['location_analysis']['location_name']}",
                            "lat": analysis['gps_data']['lat'],
                            "lon": analysis['gps_data']['lon'],
                            "source": "pic2map_visual",
                            "severity": "medium",
                            "confidence": analysis['confidence_score'],
                            "timestamp": time.time(),
                            "visual_intel": analysis
                        }
                        producer.send(OUTPUT_TOPIC, signal_msg)
                        logger.info(f"Generated new geo-signal from image: {analysis['event_id']}")
                        
                    # Also push to the specialized enriched image topic
                    producer.send(ENRICHED_TOPIC, analysis)
                    
        except Exception as e:
            logger.critical(f"Fatal error in Pic2Map Integrator: {e}")
            sys.exit(1)
        finally:
            logger.info("Pic2Map integration stopped")

if __name__ == "__main__":
    integrator = Pic2MapIntegrator()
    integrator.run()
