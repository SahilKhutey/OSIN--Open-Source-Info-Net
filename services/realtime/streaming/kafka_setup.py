"""
OSIN Real-Time Event Streaming Setup
Kafka configuration for live intelligence data
"""

from confluent_kafka import Producer, Consumer, KafkaError
import json
import logging
from typing import Dict, Any, Callable
from datetime import datetime

logger = logging.getLogger("osin-kafka")

class OSINKafkaProducer:
    def __init__(self, bootstrap_servers: str = 'localhost:9092'):
        self.conf = {
            'bootstrap.servers': bootstrap_servers,
            'client.id': 'osin-producer',
            'acks': 'all',
            'retries': 3
        }
        self.producer = Producer(self.conf)
        self.topic = 'osin-events'
    
    def publish_event(self, event_type: str, data: Dict[str, Any], 
                     source_module: str, confidence: float = 0.8):
        """Publish an event to the OSIN stream"""
        event = {
            'id': f"event_{datetime.now().timestamp()}_{hash(str(data))}",
            'type': event_type,
            'timestamp': datetime.now().isoformat(),
            'source_module': source_module,
            'confidence': confidence,
            'data': data
        }
        
        try:
            self.producer.produce(
                self.topic,
                key=event['id'],
                value=json.dumps(event),
                callback=self._delivery_report
            )
            self.producer.poll(0)
            logger.info(f"Published event: {event['id']}")
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
    
    def _delivery_report(self, err, msg):
        """Delivery callback"""
        if err is not None:
            logger.error(f"Message delivery failed: {err}")
        else:
            logger.debug(f"Message delivered to {msg.topic()} [{msg.partition()}]")

class OSINKafkaConsumer:
    def __init__(self, bootstrap_servers: str = 'localhost:9092', 
                 group_id: str = 'osin-consumer-group'):
        self.conf = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': True
        }
        self.consumer = Consumer(self.conf)
        self.topic = 'osin-events'
        self.handlers = {}
    
    def subscribe(self):
        """Subscribe to OSIN events topic"""
        self.consumer.subscribe([self.topic])
        logger.info(f"Subscribed to topic: {self.topic}")
    
    def register_handler(self, event_type: str, handler: Callable):
        """Register handler for specific event types"""
        self.handlers[event_type] = handler
        logger.info(f"Registered handler for event type: {event_type}")
    
    def start_consuming(self):
        """Start consuming events and processing with registered handlers"""
        logger.info("Starting Kafka consumer")
        try:
            while True:
                msg = self.consumer.poll(1.0)
                
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        logger.error(f"Kafka error: {msg.error()}")
                        continue
                
                try:
                    event = json.loads(msg.value().decode('utf-8'))
                    event_type = event.get('type')
                    
                    if event_type in self.handlers:
                        self.handlers[event_type](event)
                    else:
                        logger.warning(f"No handler for event type: {event_type}")
                
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
        
        except KeyboardInterrupt:
            logger.info("Stopping consumer")
        finally:
            self.consumer.close()
