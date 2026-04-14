"""
OSIN Stream Processing with Apache Flink
Real-time event enrichment and multi-stage filtering
"""

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer
from pyflink.common.serialization import JsonRowDeserializationSchema
from pyflink.common.typeinfo import Types
from pyflink.common import WatermarkStrategy, Row
from datetime import datetime
import json

class OSINFlinkProcessor:
    def __init__(self):
        self.env = StreamExecutionEnvironment.get_execution_environment()
        self.env.set_parallelism(1)
    
    def setup_kafka_source(self, bootstrap_servers: str, topic: str):
        """Set up JSON Kafka source for intelligence events"""
        deserialization_schema = JsonRowDeserializationSchema.builder() \
            .type_info(Types.ROW([
                Types.STRING(), # id
                Types.STRING(), # type
                Types.STRING(), # timestamp
                Types.STRING(), # source_module
                Types.DOUBLE(), # confidence
                Types.STRING()  # data (JSON string)
            ])).build()
        
        kafka_source = KafkaSource.builder() \
            .set_bootstrap_servers(bootstrap_servers) \
            .set_topics(topic) \
            .set_group_id("osin-flink-group") \
            .set_starting_offsets(KafkaOffsetsInitializer.earliest()) \
            .set_value_only_deserializer(deserialization_schema) \
            .build()
        
        return self.env.from_source(
            kafka_source,
            WatermarkStrategy.for_monotonous_timestamps(),
            "Kafka Source"
        )
    
    def create_pipeline(self, bootstrap_servers: str = 'localhost:9092'):
        """Build the stream processing pipeline: Parse -> Filter -> Enrich"""
        source = self.setup_kafka_source(bootstrap_servers, 'osin-events')
        
        processed = source \
            .map(lambda row: self._parse_and_enrich(row), 
                 output_type=Types.ROW([
                     Types.STRING(), Types.STRING(), Types.STRING(), 
                     Types.STRING(), Types.DOUBLE(), Types.MAP(Types.STRING(), Types.STRING())
                 ])) \
            .filter(lambda row: row[4] > 0.5) # Only High Confidence
            
        return processed
    
    def _parse_and_enrich(self, row: Row) -> Row:
        """Parse raw Kafka JSON and add server-side processing metadata"""
        try:
            data = json.loads(row[5]) if isinstance(row[5], str) else row[5]
            enriched = {**data, "processed_at": datetime.now().isoformat()}
            return Row(row[0], row[1], row[2], row[3], row[4], enriched)
        except:
            return Row(row[0], row[1], row[2], row[3], row[4], {"error": "parse_fail"})

    def execute(self):
        self.env.execute("OSIN-Stream-Processor")
