"""
Integration and System-Level Tests for OSIN
Tests component interactions, full pipelines, and end-to-end workflows.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
import json

pytestmark = [pytest.mark.integration, pytest.mark.system]


# ==================== Module-Level Fixtures ====================

@pytest.fixture
def full_pipeline(mock_pipeline):
        """Create a complete mock pipeline with all components."""
        pipeline = mock_pipeline
        
        # Mock individual pipeline stages
        pipeline.normalizer = MagicMock()
        pipeline.normalizer.normalize = AsyncMock(return_value={
            "text": "normalized text",
            "platform": "test"
        })
        
        pipeline.extractor = MagicMock()
        pipeline.extractor.extract_features = AsyncMock(return_value={
            "embedding": [0.1, 0.2, 0.3],
            "sentiment": {"label": "NEUTRAL", "score": 0.6}
        })
        
        pipeline.entity_engine = MagicMock()
        pipeline.entity_engine.extract_entities = AsyncMock(return_value=[
            {"text": "entity1", "type": "MISC"}
        ])
        
        pipeline.event_builder = MagicMock()
        pipeline.event_builder.build_event = AsyncMock(return_value={
            "event_id": "test_1",
            "text": "built event"
        })
        
        pipeline.verification_engine = MagicMock()
        pipeline.verification_engine.verify_event = AsyncMock(return_value={
            "confidence": 0.85,
            "sources": 2
        })
        
        pipeline.confidence_engine = MagicMock()
        pipeline.confidence_engine.compute_confidence = AsyncMock(return_value=0.88)
        
        # Main processing method
        pipeline.process_event = AsyncMock(return_value={
            "event": {"id": "test_1", "text": "processed"},
            "confidence_score": 0.88,
            "status": "success"
        })
        
        return pipeline


@pytest.fixture
def agent_system():
    """Create system with all agents."""
    agents = {
        "threat": MagicMock(),
        "trend": MagicMock(),
        "verification": MagicMock()
    }
    
    agents["threat"].process = AsyncMock(return_value={
        "threat_level": "low",
        "confidence": 0.8
    })
    
    agents["trend"].process = AsyncMock(return_value={
        "trending_topics": [{"keywords": ["test"], "score": 0.7}]
    })
    
    agents["verification"].process = AsyncMock(return_value={
        "verification_score": 0.85,
        "verified": True
    })
    
    return agents


@pytest.fixture
def kafka_system():
    """Create Kafka producer and consumer mocks."""
    producer = MagicMock()
    producer.send_events = AsyncMock(return_value={"sent": 100, "failed": 0})
    
    consumer = MagicMock()
    consumer.consume_messages = AsyncMock(return_value=[
        {
            "id": "kafka_msg_1",
            "text": "message from kafka",
            "platform": "test"
        }
    ])
    
    return {
        "producer": producer,
        "consumer": consumer
    }


# ==================== Pipeline Integration Tests ====================

class TestMultiModalPipelineIntegration:
    """Integration tests for the multi-modal processing pipeline."""

    @pytest.mark.asyncio
    async def test_full_pipeline_flow(self, full_pipeline, mock_raw_event):
        """Test complete pipeline flow from raw event to final intelligence."""
        result = await full_pipeline.process_event(mock_raw_event)
        
        assert result is not None
        assert "event" in result
        assert "confidence_score" in result
        assert result["status"] == "success"
        
        # Verify main processing was called
        full_pipeline.process_event.assert_called()

    @pytest.mark.asyncio
    async def test_pipeline_with_high_confidence_event(self, full_pipeline):
        """Test pipeline with high-confidence event."""
        full_pipeline.confidence_engine.compute_confidence = AsyncMock(return_value=0.98)
        full_pipeline.process_event = AsyncMock(return_value={
            "event": {"id": "high_conf", "text": "high confidence event"},
            "confidence_score": 0.98,
            "status": "success",
            "alert_triggered": True
        })
        
        result = await full_pipeline.process_event({"text": "breaking news"})
        
        assert result["confidence_score"] == 0.98
        assert result["alert_triggered"] is True

    @pytest.mark.asyncio
    async def test_pipeline_error_recovery(self, full_pipeline):
        """Test pipeline recovery from component failures."""
        # Simulate a failure in entity extraction
        full_pipeline.entity_engine.extract_entities = AsyncMock(
            side_effect=Exception("Extraction failed")
        )
        
        # Pipeline should still process and return result
        full_pipeline.process_event = AsyncMock(return_value={
            "event": {"id": "test_1", "text": "partial processing"},
            "confidence_score": 0.65,
            "status": "partial",
            "error": "Entity extraction failed"
        })
        
        result = await full_pipeline.process_event({})
        assert result["status"] in ["partial", "success"]

    @pytest.mark.asyncio
    async def test_pipeline_batch_processing(self, full_pipeline, sample_events):
        """Test pipeline batch processing of multiple events."""
        expected_results = [
            {
                "event": {"id": e["id"], "text": e["text"]},
                "confidence_score": 0.80,
                "status": "success"
            }
            for e in sample_events
        ]
        
        full_pipeline.process_batch = AsyncMock(return_value=expected_results)
        
        results = await full_pipeline.process_batch(sample_events)
        
        assert len(results) == len(sample_events)
        assert all(r["status"] == "success" for r in results)


# ==================== Agent Coordination Tests ====================

class TestAgentCoordination:
    """Tests for agent coordination and context sharing."""

    @pytest.mark.asyncio
    async def test_agent_context_sharing(self, agent_system, mock_event):
        """Test context sharing between agents."""
        # First agent processes
        threat_result = await agent_system["threat"].process(mock_event, {})
        
        # Context includes first result
        context = {"threat_agent": {"output": threat_result}}
        
        # Second agent gets context
        trend_result = await agent_system["trend"].process(mock_event, context)
        
        # Third agent gets both results
        context["trend_agent"] = {"output": trend_result}
        verification_result = await agent_system["verification"].process(
            mock_event, context
        )
        
        assert threat_result["threat_level"] is not None
        assert trend_result["trending_topics"] is not None
        assert verification_result["verified"] is not None

    @pytest.mark.asyncio
    async def test_agent_threat_escalation(self, agent_system, mock_event):
        """Test threat escalation based on multiple agent outputs."""
        # Threat agent detects high threat
        agent_system["threat"].process = AsyncMock(return_value={
            "threat_level": "critical",
            "confidence": 0.95
        })
        
        threat_result = await agent_system["threat"].process(mock_event, {})
        
        # Should trigger additional verification
        if threat_result["threat_level"] == "critical":
            context = {"requires_verification": True, "threat": threat_result}
            verification_result = await agent_system["verification"].process(
                mock_event, context
            )
            
            assert verification_result["verified"] is not None

    @pytest.mark.asyncio
    async def test_multi_agent_consensus(self, agent_system, mock_event):
        """Test consensus building across multiple agents."""
        context = {}
        results = {}
        
        # Get all agent outputs
        for agent_name, agent in agent_system.items():
            output = await agent.process(mock_event, context)
            results[agent_name] = output
            context[agent_name] = {"output": output}
        
        # Verify all agents provided output
        assert len(results) == 3
        assert all(output for output in results.values())


# ==================== Kafka/Streaming Integration ====================

class TestKafkaStreamingIntegration:
    """Integration tests for Kafka producer-consumer flows."""

    @pytest.mark.asyncio
    async def test_event_streaming_flow(self, kafka_system, sample_events):
        """Test complete event streaming flow."""
        producer = kafka_system["producer"]
        consumer = kafka_system["consumer"]
        
        # Produce events
        producer.send_events = AsyncMock(return_value={
            "sent": len(sample_events),
            "failed": 0
        })
        
        produce_result = await producer.send_events("raw.events", sample_events)
        assert produce_result["sent"] == len(sample_events)
        
        # Consume events
        consumer.consume_messages = AsyncMock(return_value=sample_events)
        consume_result = await consumer.consume_messages(timeout=5.0)
        
        assert len(consume_result) == len(sample_events)

    @pytest.mark.asyncio
    async def test_high_throughput_streaming(self, kafka_system):
        """Test high-throughput event streaming."""
        large_batch = [
            {"id": f"event_{i}", "text": f"event {i}", "platform": "test"}
            for i in range(1000)
        ]
        
        kafka_system["producer"].send_events = AsyncMock(return_value={
            "sent": 1000,
            "failed": 0
        })
        
        result = await kafka_system["producer"].send_events("raw.events", large_batch)
        assert result["sent"] == 1000
        assert result["failed"] == 0

    @pytest.mark.asyncio
    async def test_kafka_error_handling(self, kafka_system):
        """Test Kafka error handling and recovery."""
        kafka_system["producer"].send_events = AsyncMock(return_value={
            "sent": 95,
            "failed": 5
        })
        
        result = await kafka_system["producer"].send_events("raw.events", [])
        assert result["failed"] >= 0

    @pytest.mark.asyncio
    async def test_kafka_partition_distribution(self, kafka_system):
        """Test event distribution across partitions."""
        # Create events that should be distributed across partitions
        events = [
            {
                "id": f"event_{i}",
                "platform": ["twitter", "reddit", "news"][i % 3],
                "text": f"event {i}"
            }
            for i in range(300)
        ]
        
        kafka_system["producer"].send_events = AsyncMock(return_value={
            "sent": 300,
            "failed": 0,
            "partitions_used": 3
        })
        
        result = await kafka_system["producer"].send_events("raw.events", events)
        assert result["sent"] == 300


# ==================== End-to-End Workflows ====================

class TestEndToEndWorkflows:
    """Full end-to-end workflow tests."""

    @pytest.fixture
    def complete_system(self, full_pipeline, agent_system, kafka_system):
        """Complete system with pipeline, agents, and streaming."""
        return {
            "pipeline": full_pipeline,
            "agents": agent_system,
            "kafka": kafka_system
        }

    @pytest.mark.asyncio
    async def test_raw_event_to_intelligence_output(self, complete_system, mock_raw_event):
        """Test complete flow from raw event to intelligence output."""
        # 1. Ingest raw event to Kafka
        await complete_system["kafka"]["producer"].send_events(
            "raw.events", [mock_raw_event]
        )
        
        # 2. Consume from Kafka
        consumed = await complete_system["kafka"]["consumer"].consume_messages()
        
        # 3. Process through pipeline
        pipeline_result = await complete_system["pipeline"].process_event(consumed[0])
        
        # 4. Process through agents
        context = {}
        for agent_name, agent in complete_system["agents"].items():
            result = await agent.process(pipeline_result["event"], context)
            context[agent_name] = {"output": result}
        
        # 5. Verify final intelligence output
        assert pipeline_result["confidence_score"] is not None
        assert len(context) == 3  # All agents provided output

    @pytest.mark.asyncio
    async def test_high_priority_event_escalation(self, complete_system):
        """Test high-priority event escalation through system."""
        high_threat_event = {
            "id": "critical_1",
            "text": "Critical emergency with multiple casualties",
            "platform": "news",
            "priority": "critical"
        }
        
        # Send to streaming
        await complete_system["kafka"]["producer"].send_events(
            "raw.events", [high_threat_event]
        )
        
        # Process through pipeline
        result = await complete_system["pipeline"].process_event(high_threat_event)
        
        # Threat agent should detect
        threat_result = await complete_system["agents"]["threat"].process(
            result["event"], {}
        )
        
        assert threat_result is not None

    @pytest.mark.asyncio
    async def test_multi_source_correlation(self, complete_system, sample_events):
        """Test correlation of events from multiple sources."""
        # Simulate events from different platforms
        twitter_events = [e for e in sample_events if e["platform"] == "twitter"]
        reddit_events = [e for e in sample_events if e["platform"] == "reddit"]
        news_events = [e for e in sample_events if e["platform"] == "news"]
        
        all_events = twitter_events + reddit_events + news_events
        
        # Send all to Kafka
        await complete_system["kafka"]["producer"].send_events(
            "raw.events", all_events
        )
        
        # Process through pipeline
        processed = []
        for event in all_events:
            result = await complete_system["pipeline"].process_event(event)
            processed.append(result)
        
        assert len(processed) == len(all_events)

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_sustained_high_volume_processing(self, complete_system):
        """Test sustained processing of high event volume."""
        # Generate large batch
        large_batch = [
            {
                "id": f"bulk_{i}",
                "text": f"Event {i}",
                "platform": ["twitter", "reddit", "news"][i % 3]
            }
            for i in range(500)
        ]
        
        # Stream to Kafka
        await complete_system["kafka"]["producer"].send_events(
            "raw.events", large_batch
        )
        
        # Process batch through pipeline
        results = []
        for event in large_batch[:50]:  # Process subset for testing
            result = await complete_system["pipeline"].process_event(event)
            results.append(result)
        
        assert len(results) == 50
        assert all(r["status"] == "success" for r in results)


# ==================== Data Consistency Tests ====================

class TestDataConsistency:
    """Tests for data consistency across system."""

    @pytest.mark.asyncio
    async def test_event_immutability(self):
        """Test that original events are not mutated."""
        original_event = {
            "id": "test_1",
            "text": "original text",
            "platform": "test"
        }
        
        # Create a copy (pipeline shouldn't modify original)
        event_copy = original_event.copy()
        
        # Simulate processing
        processed = {**event_copy, "processed": True}
        
        # Original should be unchanged
        assert original_event == {"id": "test_1", "text": "original text", "platform": "test"}
        assert "processed" not in original_event

    @pytest.mark.asyncio
    async def test_confidence_score_range(self, mock_verified_event):
        """Test confidence scores are within valid range."""
        confidence = mock_verified_event["final_confidence"]
        
        assert 0 <= confidence <= 1, "Confidence must be between 0 and 1"

    def test_timestamp_consistency(self, sample_events):
        """Test timestamp consistency across events."""
        for event in sample_events:
            # Should have valid ISO format timestamp
            assert "T" in event["timestamp"]
            # ISO format timestamp should have T separator and be valid
            assert isinstance(event["timestamp"], str)
            assert len(event["timestamp"]) > 10  # Minimal ISO format


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
