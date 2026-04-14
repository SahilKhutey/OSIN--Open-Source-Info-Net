import logging
from kafka.admin import KafkaAdminClient, NewTopic
import time
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

def initialize_topics():
    """Initializes the OSIN internal message bus topics"""
    admin_client = None
    max_retries = 10
    retry_delay = 5

    # Wait for Kafka to be ready
    for i in range(max_retries):
        try:
            admin_client = KafkaAdminClient(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                client_id='osin-topic-manager'
            )
            logger.info("Successfully connected to Kafka Broker")
            break
        except Exception as e:
            logger.warning(f"Failed to connect to Kafka (Attempt {i+1}/{max_retries}): {e}")
            time.sleep(retry_delay)
    
    if not admin_client:
        logger.error("Could not connect to Kafka Broker. Exiting.")
        return

    # Define OSIN topics
    # Format: [name, partitions, replication_factor]
    osin_topics = [
        # Raw Data Ingestion
        NewTopic(name="osin.raw.satellite", num_partitions=3, replication_factor=1),
        NewTopic(name="osin.raw.social", num_partitions=3, replication_factor=1),
        
        # Processed Data
        NewTopic(name="osin.processed.nlp", num_partitions=3, replication_factor=1),
        NewTopic(name="osin.processed.cv", num_partitions=3, replication_factor=1),
        
        # High-Fidelity Intelligence (Correlated)
        NewTopic(name="osin.intelligence.events", num_partitions=3, replication_factor=1),
        NewTopic(name="osin.intelligence.correlations", num_partitions=3, replication_factor=1)
    ]

    try:
        existing_topics = admin_client.list_topics()
        topics_to_create = [t for t in osin_topics if t.name not in existing_topics]
        
        if topics_to_create:
            admin_client.create_topics(new_topics=topics_to_create, validate_only=False)
            for topic in topics_to_create:
                logger.info(f"Created topic: {topic.name}")
        else:
            logger.info("All OSIN topics already exist.")
            
    except Exception as e:
        logger.error(f"Error initializing topics: {e}")
    finally:
        admin_client.close()

if __name__ == "__main__":
    initialize_topics()
