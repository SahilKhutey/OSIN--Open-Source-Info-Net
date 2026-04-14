import os
import time
import json
import logging
from kafka import KafkaConsumer
from transformers import pipeline
from server.lib.tracing.trace_manager import TraceManager, traced
from server.lib.producers.enhanced_producer import EnhancedProducer
from server.lib.backpressure.backpressure_manager import BackpressureManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NLPProcessor")

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")
INPUT_TOPIC = "osin.raw.social"
OUTPUT_TOPIC = "osin.processed.nlp"
SERVICE_NAME = "nlp-processor"

@traced(SERVICE_NAME, "analyze_sentiment")
def analyze_sentiment(nlp_pipeline, text, _trace_context=None):
    """Execution span for intelligence analysis"""
    return nlp_pipeline(text)

def main():
    # Initialize SVP-2 Enhanced Components
    producer = EnhancedProducer(KAFKA_BOOTSTRAP_SERVERS, SERVICE_NAME)
    backpressure = BackpressureManager(service_name=SERVICE_NAME)
    
    # Initialize Kafka Consumer
    consumer = None
    while not consumer:
        try:
            consumer = KafkaConsumer(
                INPUT_TOPIC,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                group_id='osin-nlp-group',
                auto_offset_reset='latest'
            )
            logger.info("Connected to Kafka Consumer")
        except Exception as e:
            logger.warning(f"Waiting for Kafka... {e}")
            time.sleep(5)

    # Initialize AI Pipeline
    logger.info("Initializing NLP Pipeline...")
    nlp = pipeline("sentiment-analysis", model="lxyuan/distilbert-base-multilingual-cased-sentiments-student")
    
    logger.info(f"OSIN {SERVICE_NAME} Started with SVP-2 Enhancements")
    
    for message in consumer:
        try:
            # SVP-2 Backpressure Protection
            backpressure.check_and_throttle()
            
            data = message.value
            text = data.get('text', '')
            
            # SVP-1/2 Distributed Tracing: Extract parent context
            parent_trace = data.get('_trace')
            
            if text:
                # Run Traced Intelligence Analysis
                results = analyze_sentiment(nlp, text, _trace_context=parent_trace)
                sentiment = results[0]
                
                # Enrich data
                processed_event = {
                    "original_id": data.get('id'),
                    "source": data.get('source'),
                    "processed_type": "nlp_sentiment",
                    "intelligence": {
                        "sentiment": sentiment['label'],
                        "score": round(sentiment['score'], 4)
                    },
                    "timestamp": data.get('timestamp')
                }
                
                # Propagate Trace to Next Service
                producer.send_traced(OUTPUT_TOPIC, processed_event, parent_context=parent_trace)
                logger.info(f"Processed Intelligence: {processed_event['original_id']} -> {sentiment['label']}")
                
        except Exception as e:
            logger.error(f"Error in NLP processing: {e}")

if __name__ == "__main__":
    main()
