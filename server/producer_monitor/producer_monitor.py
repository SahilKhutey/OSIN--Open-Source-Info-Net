import time
import json
import logging
from kafka import KafkaProducer
from prometheus_client import Counter, Gauge

# Configure monitoring logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("osin-svp1-producer")

# Metrics definitions
PRODUCER_MESSAGES = Counter('osin_producer_messages_total', 'Total messages produced', ['producer', 'topic'])
PRODUCER_ERRORS = Counter('osin_producer_errors_total', 'Total producer errors', ['producer'])
PRODUCER_LATENCY = Gauge('osin_producer_latency_ms', 'Latest producer latency in MS', ['producer'])

class MonitoredProducer:
    """
    SVP-1 Compliant Producer Wrapper.
    Adds operational metrics and structured logging to existing OSIN data producers.
    """
    def __init__(self, producer_name: str, bootstrap_servers: str = 'kafka:29092'):
        self.producer_name = producer_name
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all',
            retries=5
        )
        logger.info(f"Initialized MonitoredProducer: {producer_name}")
    
    def send_intelligence(self, topic: str, payload: dict):
        """Send message with full observability telemetry"""
        start_time = time.time()
        
        try:
            # Inject metadata for SVP-1 traceability
            payload['_svp1_meta'] = {
                "producer": self.producer_name,
                "timestamp": time.time(),
                "trace_id": payload.get('id', f"gen_{int(time.time())}")
            }
            
            future = self.producer.send(topic, payload)
            # Synchronous wait for confirmation in SVP-1 mode
            future.get(timeout=10)
            
            latency = (time.time() - start_time) * 1000
            PRODUCER_LATENCY.labels(producer=self.producer_name).set(latency)
            PRODUCER_MESSAGES.labels(producer=self.producer_name, topic=topic).inc()
            
            logger.debug(f"[{self.producer_name}] Produced to {topic}: Latency {latency:.2f}ms")
            return True
            
        except Exception as e:
            PRODUCER_ERRORS.labels(producer=self.producer_name).inc()
            logger.error(f"[{self.producer_name}] CRITICAL PRODUCTION ERROR on {topic}: {e}")
            return False
    
    def flush(self):
        self.producer.flush()

    def close(self):
        self.producer.close()

# For HEARTBEAT integration
def start_heartbeat_loop(producer: MonitoredProducer, interval: int = 60):
    """Fires periodic system heartbeats into the intelligence bus"""
    import threading
    def loop():
        while True:
            producer.send_intelligence("osin.health.check", {
                "type": "heartbeat",
                "status": "active",
                "uptime": time.process_time()
            })
            time.sleep(interval)
    
    thread = threading.Thread(target=loop, daemon=True)
    thread.start()
    return thread
