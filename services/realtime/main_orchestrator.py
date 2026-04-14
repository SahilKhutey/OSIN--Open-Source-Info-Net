"""
OSIN Real-Time Intelligence Orchestrator
Main coordination service for Kafka, Flink, AI Reasoning, and ML Prediction
"""

import asyncio
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime

from .streaming.kafka_setup import OSINKafkaConsumer, OSINKafkaProducer
from .graph_core.streaming_graph import StreamingGraphEngine
from .ai.reasoning_engine import AIReasoningEngine
from .prediction.threat_predictor import ThreatPredictor

# Need to access Graph Intelligence entities/architecture
# Assuming service-to-service communication or shared persistence
# For the orchestrator, we'll initialize localized engines

app = FastAPI(title="OSIN Real-Time Orchestrator", version="4.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class OSINOrchestrator:
    def __init__(self):
        self.kafka_consumer = OSINKafkaConsumer()
        self.kafka_producer = OSINKafkaProducer()
        
        # Integration with existing Graph Builder (mocked here but would use shared DB in prod)
        # Assuming we have a way to access the entity store
        from services.graph_core.graph_builder import OSINGraphBuilder
        self.graph_builder = OSINGraphBuilder()
        
        self.streaming_graph = StreamingGraphEngine(
            self.graph_builder.entity_store,
            self.graph_builder.relationship_engine,
            self.graph_builder.similarity_engine
        )
        
        self.ai_engine = AIReasoningEngine(
            self.graph_builder.entity_store,
            self.graph_builder.relationship_engine,
            openai_api_key="sk-..." # Should be loaded from ENV
        )
        
        self.threat_predictor = ThreatPredictor(self.graph_builder.entity_store)
        self.is_running = False

    async def start(self):
        self.is_running = True
        # 1. Register Kafka Handlers for all 15 layers
        for layer in ['geo', 'cyber', 'audio', 'image', 'signal', 'threat']:
            self.kafka_consumer.register_handler(layer, self._handle_event)
        
        # 2. Start Background Reasoning Loop
        asyncio.create_task(self.streaming_graph.process_event_stream())
        
        # 3. Start Kafka Consumer Thread
        asyncio.create_task(self._kafka_poll_loop())
        
        # 4. Periodic ML Retraining
        asyncio.create_task(self._ml_retraining_loop())

    async def _handle_event(self, event):
        await self.streaming_graph.event_queue.put(event)

    async def _kafka_poll_loop(self):
        self.kafka_consumer.subscribe()
        while self.is_running:
            self.kafka_consumer.start_consuming()
            await asyncio.sleep(0.1)

    async def _ml_retraining_loop(self):
        while self.is_running:
            self.threat_predictor.train_models()
            await asyncio.sleep(3600) # Every hour

orchestrator = OSINOrchestrator()

@app.on_event("startup")
async def startup():
    await orchestrator.start()

@app.get("/status")
async def get_status():
    return {
        "status": "RUNNING",
        "entities": orchestrator.graph_builder.entity_store.get_entity_count(),
        "predictions": orchestrator.threat_predictor.prediction_history[-1:]
    }

@app.get("/threat-prediction")
async def get_prediction():
    return orchestrator.threat_predictor.predict_future_intensity()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8021)
