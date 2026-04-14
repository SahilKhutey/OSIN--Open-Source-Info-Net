#!/usr/bin/env python3
"""
OSIN Deduplication Pipeline Integration
Connects entity extraction to deduplication service via Kafka
"""

import json
import requests
import logging
import time
import os
import signal
import sys
from kafka import KafkaConsumer, KafkaProducer
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("osin-deduplication-integration")

# Configuration via environment variables
DEDUPLICATION_SERVICE = os.getenv("DEDUPLICATION_SERVICE", "http://osin-deduplication:8002/deduplicate")
KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "localhost:9092,kafka-broker:9092").split(",")
INPUT_TOPIC = os.getenv("INPUT_TOPIC", "osin-entities")
OUTPUT_TOPIC = os.getenv("OUTPUT_TOPIC", "osin-deduplicated")
ERROR_TOPIC = os.getenv("ERROR_TOPIC", "osin-deduplication-errors")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "100"))
BATCH_TIMEOUT = int(os.getenv("BATCH_TIMEOUT", "5")) # seconds

class DeduplicationIntegrator:
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
                group_id="osin-deduplication-group",
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                auto_offset_reset='latest',
                enable_auto_commit=True,
                auto_commit_interval_ms=5000,
                max_poll_records=BATCH_SIZE
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
            logger.error(f"Failed to create Kafka clients: {e}")
            raise
    
    def send_to_deduplication(self, events: List[Dict]) -> Dict:
        """Send events to deduplication service"""
        try:
            payload = {
                "events": events,
                "batch_id": f"batch_{int(time.time())}_{len(events)}"
            }
            
            response = requests.post(
                DEDUPLICATION_SERVICE,
                json=payload,
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Deduplication service error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during deduplication: {e}")
            raise
    
    def process_batch(self, batch: List[Dict], producer: KafkaProducer):
        """Process a batch of events"""
        if not batch:
            return
        
        try:
            # Send to deduplication service
            result = self.send_to_deduplication(batch)
            
            # Process each cluster
            for cluster in result.get('clusters', []):
                if not cluster:
                    continue
                
                # Use first event as representative
                representative_id = cluster[0]
                representative = next(
                    (event for event in batch if event['id'] == representative_id),
                    None
                )
                
                if representative:
                    # Add cluster metadata
                    representative['cluster_metadata'] = {
                        'cluster_ids': cluster,
                        'cluster_size': len(cluster),
                        'deduplication_batch_id': result.get('batch_id'),
                        'processing_time_ms': result.get('processing_time_ms'),
                        'similarity_threshold': result.get('similarity_threshold')
                    }
                    
                    # Send to output topic
                    producer.send(OUTPUT_TOPIC, representative)
                    logger.debug(f"Sent clustered event: {representative['id']}")
            
            logger.info(
                f"Processed batch: {result.get('unique_events', 0)} "
                f"unique from {result.get('total_events', 0)} events "
                f"in {result.get('processing_time_ms', 0):.2f}ms"
            )
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            # Send failed events to error topic
            for event in batch:
                try:
                    error_event = event.copy()
                    error_event['error'] = str(e)
                    error_event['error_timestamp'] = time.time()
                    producer.send(ERROR_TOPIC, error_event)
                except Exception as inner_e:
                    logger.error(f"Failed to send error event: {inner_e}")
    
    def run(self):
        """Main processing loop"""
        logger.info("Starting OSIN Deduplication Integration v2.1.0")
        
        try:
            consumer, producer = self.create_kafka_clients()
            logger.info("Kafka clients initialized successfully")
            
            batch = []
            last_batch_time = time.time()
            
            while self.running:
                try:
                    # Poll for messages
                    messages = consumer.poll(timeout_ms=1000, max_records=BATCH_SIZE)
                    
                    if messages:
                        for topic_partition, msg_list in messages.items():
                            for message in msg_list:
                                if message.value:
                                    batch.append(message.value)
                                    logger.debug(f"Received event: {message.value.get('id', 'unknown')}")
                    
                    # Process batch if size or timeout reached
                    current_time = time.time()
                    if (len(batch) >= BATCH_SIZE or 
                        (batch and current_time - last_batch_time >= BATCH_TIMEOUT)):
                        
                        self.process_batch(batch, producer)
                        batch = []
                        last_batch_time = current_time
                        producer.flush()
                    
                except Exception as e:
                    logger.error(f"Error in processing loop: {e}")
                    time.sleep(1)  # Prevent tight loop on errors
            
            # Process remaining batch on shutdown
            if batch:
                logger.info(f"Processing final batch of {len(batch)} events...")
                self.process_batch(batch, producer)
                producer.flush()
                
        except Exception as e:
            logger.critical(f"Fatal error in Deduplication Integrator: {e}")
            sys.exit(1)
        
        finally:
            logger.info("Deduplication integration stopped")

if __name__ == "__main__":
    integrator = DeduplicationIntegrator()
    integrator.run()
