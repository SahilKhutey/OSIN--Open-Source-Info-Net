import json
from aiokafka import AIOKafkaProducer
from app.config import settings

class KafkaProducerManager:
    def __init__(self):
        self.producer = None

    async def start(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers, # Use instance attribute
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            security_protocol=self.security_protocol, # Add SSL parameters
            ssl_cafile=self.ssl_cafile,
            ssl_certfile=self.ssl_certfile,
            ssl_keyfile=self.ssl_keyfile
        )
        await self.producer.start()

    async def stop(self):
        if self.producer:
            await self.producer.stop()

    async def send(self, topic: str, data: dict): # Renamed from send_signal, changed signal_data to data
        if not self.producer:
            await self.start()
        await self.producer.send_and_wait(topic, data) # Use 'data' here

kafka_producer = KafkaProducerManager()
