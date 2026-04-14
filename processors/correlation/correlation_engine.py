import os
import time
import json
import logging
from kafka import KafkaProducer, KafkaConsumer
from math import radians, cos, sin, asin, sqrt
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")
INPUT_TOPICS = ["osin.processed.nlp", "osin.processed.cv"]
OUTPUT_TOPIC = "osin.intelligence.correlations"

class CorrelationEngine:
    def __init__(self):
        self.event_buffer = []
        self.time_window = 3600  # 1 hour window for correlation
        
    def haversine(self, lon1, lat1, lon2, lat2):
        """Calculate the great circle distance between two points on earth"""
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371 # Radius of earth in kilometers
        return c * r

    def correlate(self, new_event):
        """Find correlations between new_event and previous events"""
        correlations = []
        
        for old_event in self.event_buffer:
            score = 0
            reasons = []
            
            # 1. Temporal Correlation
            t1 = datetime.fromisoformat(new_event['timestamp'])
            t2 = datetime.fromisoformat(old_event['timestamp'])
            time_diff = abs((t1 - t2).total_seconds())
            
            if time_diff < 1800: # 30 mins
                score += 0.3
                reasons.append("temporal_proximity")
                
            # 2. Spatial Correlation (if coordinates exist)
            coord1 = new_event.get('coordinates')
            coord2 = old_event.get('coordinates')
            if coord1 and coord2:
                dist = self.haversine(coord1[0], coord1[1], coord2[0], coord2[1])
                if dist < 50: # 50km
                    score += 0.4
                    reasons.append("spatial_proximity")
            
            # 3. Semantic Correlation (Placeholder for actual similarity)
            # In v9, this would use vector embeddings from Neo4j/Pinecone
            if new_event['source'] != old_event['source']:
                score += 0.2
                reasons.append("cross_platform_validation")
                
            if score >= 0.5:
                correlations.append({
                    "event_a": new_event['original_id'],
                    "event_b": old_event['original_id'],
                    "confidence": score,
                    "reasons": reasons
                })
                
        return correlations

def main():
    engine = CorrelationEngine()
    
    # Initialize Kafka Consumer
    consumer = None
    while not consumer:
        try:
            consumer = KafkaConsumer(
                *INPUT_TOPICS,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                group_id='osin-correlation-group',
                auto_offset_reset='latest'
            )
            logger.info("Connected to Kafka Consumer")
        except Exception as e:
            logger.warning(f"Waiting for Kafka... {e}")
            time.sleep(5)

    # Initialize Kafka Producer
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    logger.info("OSIN Correlation Engine Started")
    
    for message in consumer:
        try:
            new_event = message.value
            correlations = engine.correlate(new_event)
            
            for corr in correlations:
                producer.send(OUTPUT_TOPIC, corr)
                logger.info(f"Correlation Detected: {corr['event_a']} <-> {corr['event_b']} ({corr['confidence']})")
            
            # Add to buffer and prune old events
            engine.event_buffer.append(new_event)
            current_time = datetime.utcnow()
            engine.event_buffer = [
                e for e in engine.event_buffer 
                if (current_time - datetime.fromisoformat(e['timestamp'])).total_seconds() < engine.time_window
            ]
                
        except Exception as e:
            logger.error(f"Error in Correlation processing: {e}")

if __name__ == "__main__":
    main()
