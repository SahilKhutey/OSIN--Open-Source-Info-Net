import json
import asyncio
from app.db.database import AsyncSessionLocal
from app.db.models import Signal, Trend
from app.ai.nlp_engine import nlp_engine
from app.ai.credibility import credibility_scorer
from app.ai.military_processor import military_processor
from app.ai.combat_credibility import combat_credibility_engine
from app.ai.warfare_analyser import warfare_analyser
from app.ai.translator import translator
from app.ai.imagery import imagery_analysis
from app.ai.sigint import sigint_processor
from app.streaming.kafka_producer import kafka_producer
from sqlalchemy import select, func

class SignalProcessor:
    def __init__(self):
        self.is_running = True

    async def clean_signal(self, raw_data: dict) -> dict:
        """
        Normalize raw data from various sources into a unified structure.
        """
        content = raw_data.get("content", "") or raw_data.get("text", "")
        source_name = raw_data.get("source_name", "unknown")
        
        # Basic cleaning: remove extra whitespace, normalize case
        clean_content = " ".join(content.split()).strip()
        
        processed_data = {
            "source_type": raw_data.get("source_type"),
            "source_name": source_name,
            "content": clean_content,
            "metadata": raw_data.get("metadata", {}),
        }
        
        # New 7-parameter credibility scoring
        cred_result = credibility_scorer.score_event(clean_content, processed_data["metadata"])
        
        # Phase 2: Military-Grade Triage and Combat-Ready Assessment
        threat_assessment = await military_processor.process_event(processed_data)
        combat_score = combat_credibility_engine.calculate_combat_score(processed_data)
        warfare_analysis = warfare_analyser.analyze_warfare_elements(clean_content, processed_data["metadata"])
        
        processed_data["credibility_score"] = cred_result.score
        processed_data["metadata"]["credibility_breakdown"] = cred_result.breakdown
        processed_data["metadata"]["threat_level"] = threat_assessment.classification
        processed_data["metadata"]["combat_score"] = combat_score.score
        processed_data["metadata"]["combat_metrics"] = combat_score.metrics
        processed_data["metadata"]["warfare_analysis"] = warfare_analysis
        processed_data["metadata"]["projected_impact"] = threat_assessment.projected_impact
        processed_data["metadata"]["recommended_action"] = threat_assessment.recommended_action
        
        # Phase 6: Multi-Domain Intelligence Fusion
        if processed_data["metadata"].get("language") != "EN":
             translation = translator.translate_with_context(clean_content, processed_data["metadata"].get("language", "AR"))
             processed_data["metadata"]["translation"] = translation

        if "coordinates" in processed_data["metadata"]:
            coords = processed_data["metadata"]["coordinates"]
            processed_data["metadata"]["satellite_verification"] = imagery_analysis.correlate_with_physical_world(coords, "conflict")
            processed_data["metadata"]["sigint_analysis"] = sigint_processor.process_signals(coords)
        
        # Add embeddings
        processed_data["embedding"] = nlp_engine.get_embeddings(clean_content)
        
        return processed_data

    async def save_signal(self, processed_data: dict):
        async with AsyncSessionLocal() as session:
            new_signal = Signal(
                source_type=processed_data["source_type"],
                source_name=processed_data["source_name"],
                content=processed_data["content"],
                metadata_json=processed_data["metadata"]
            )
            session.add(new_signal)
            await session.commit()
            print(f"Signal saved to DB: {new_signal.id}")
            return new_signal.id

    async def detect_trends(self):
        """
        Simple trend detection: group by frequency over a window.
        In production, this would use Flink or a more complex windowed aggregator.
        """
        async with AsyncSessionLocal() as session:
            # Placeholder for trend detection logic
            # Query signals from the last hour, group by keyword extraction
            # For now, we'll just log that detection is active
            print("Running real-time trend detection cycle...")

    async def process_one(self, raw_data: dict):
        processed_data = await self.clean_signal(raw_data)
        signal_id = await self.save_signal(processed_data)
        # Further processing: push to trend detection or alert engine
        return signal_id

async def run_processor_loop():
    processor = SignalProcessor()
    # In a real setup, this would consume from Kafka
    # For now, we'll simulate a consumer loop
    while True:
        # Simulated raw signal from kafka
        raw_signal = {"source_type": "social", "content": "Sample signal showing a trending topic.", "source_name": "Twitter"}
        await processor.process_one(raw_signal)
        await asyncio.sleep(5)
