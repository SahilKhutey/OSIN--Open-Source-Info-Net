import time
import json
import logging
from kafka import KafkaConsumer
from prometheus_client import Counter, Histogram

# Configure monitoring logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("osin-svp1-consumer")

# Metrics definitions
CONSUMER_MESSAGES = Counter('osin_consumer_messages_total', 'Total messages consumed', ['consumer', 'topic'])
CONSUMER_ERRORS = Counter('osin_consumer_errors_total', 'Total consumer errors', ['consumer'])
CONSUMER_LATENCY = Histogram('osin_consumer_processing_seconds', 'Processing latency in seconds', ['consumer', 'topic'])

class MonitoredConsumer:
    """
    SVP-1 Compliant Consumer Wrapper.
    Adds processing latency histograms and error counters to OSIN intelligence processors.
    """
    def __init__(self, consumer_name: str, topics: list, group_id: str, bootstrap_servers: str = 'kafka:29092'):
        self.consumer_name = consumer_name
        self.topics = topics
        self.consumer = KafkaConsumer(
            *topics,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True
        )
        logger.info(f"Initialized MonitoredConsumer: {consumer_name} (Group: {group_id})")

    def run_pipeline(self, processor_callback):
        """Execute processing loop with automatic monitoring"""
        logger.info(f"[{self.consumer_name}] Starting intelligent processing loop...")
        
        for message in self.consumer:
            start_time = time.time()
            topic = message.topic
            
            try:
                # Log receipt
                logger.debug(f"[{self.consumer_name}] RCV: {topic} (ID: {message.value.get('id', 'N/A')})")
                
                # Execute application logic
                processor_callback(message.value)
                
                # Record metrics
                latency = time.time() - start_time
                CONSUMER_LATENCY.labels(consumer=self.consumer_name, topic=topic).observe(latency)
                CONSUMER_MESSAGES.labels(consumer=self.consumer_name, topic=topic).inc()
                
                if latency > 1.5:
                    logger.warning(f"[{self.consumer_name}] DEGRADED PERFORMANCE: {latency:.2f}s on {topic}")

            except Exception as e:
                CONSUMER_ERRORS.labels(consumer=self.consumer_name).inc()
                logger.error(f"[{self.consumer_name}] FAILURE on {topic}: {e}")
                self.handle_failure(message.value, str(e))

    def handle_failure(self, payload: dict, error: str):
        """Placeholder for Dead Letter Queue (DLQ) integration in future iterations"""
        logger.error(f"DROPPING_MESSAGE: ID {payload.get('id', 'N/A')} // Error: {error}")

def spawn_monitored_consumer(name, topics, group, processor):
    """Utility to spawn a consumer in a dedicated thread"""
    import threading
    mc = MonitoredConsumer(name, topics, group)
    thread = threading.Thread(target=mc.run_pipeline, args=(processor,), daemon=True)
    thread.start()
    return mc, thread
