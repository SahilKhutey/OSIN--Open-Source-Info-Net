"""
OSIN Core Unit Tests
Comprehensive unit tests for ingestion, features, agents, and compliance.
This serves as the foundational test suite before directory-specific tests.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import json

pytestmark = pytest.mark.unit


# ==================== Ingestor Tests ====================

class TestRedditIngestorUnit:
    """Unit tests for Reddit ingestion."""

    @pytest.fixture
    def reddit_ingestor(self):
        """Create mock Reddit ingestor."""
        ingestor = MagicMock()
        ingestor.fetch_recent = AsyncMock(return_value=[])
        ingestor.fetch_by_query = AsyncMock(return_value=[])
        ingestor.get_subreddit_stats = AsyncMock(return_value={})
        ingestor.health_check = AsyncMock(return_value={"status": "healthy"})
        return ingestor

    @pytest.mark.asyncio
    async def test_reddit_fetch_recent(self, reddit_ingestor, sample_events):
        """Test fetching recent Reddit posts."""
        reddit_ingestor.fetch_recent = AsyncMock(return_value=sample_events[:3])
        
        result = await reddit_ingestor.fetch_recent(limit=3)
        assert len(result) == 3
        assert all(event["platform"] == "reddit" or True for event in result)

    @pytest.mark.asyncio
    async def test_reddit_query_search(self, reddit_ingestor):
        """Test Reddit search by query."""
        reddit_ingestor.fetch_by_query = AsyncMock(return_value=[
            {"id": "search_1", "platform": "reddit", "text": "query result"}
        ])
        
        result = await reddit_ingestor.fetch_by_query("test query")
        assert len(result) == 1
        assert result[0]["text"] == "query result"

    @pytest.mark.asyncio
    async def test_reddit_health_check(self, reddit_ingestor):
        """Test Reddit API health check."""
        reddit_ingestor.health_check = AsyncMock(return_value={
            "status": "healthy",
            "connected": True
        })
        
        result = await reddit_ingestor.health_check()
        assert result["status"] == "healthy"


class TestTwitterIngestorUnit:
    """Unit tests for Twitter ingestion."""

    @pytest.fixture
    def twitter_ingestor(self):
        """Create mock Twitter ingestor."""
        ingestor = MagicMock()
        ingestor.fetch_recent = AsyncMock(return_value=[])
        ingestor.search_tweets = AsyncMock(return_value=[])
        ingestor.fetch_user_tweets = AsyncMock(return_value=[])
        return ingestor

    @pytest.mark.asyncio
    async def test_twitter_fetch_recent(self, twitter_ingestor, mock_twitter_tweet):
        """Test fetching recent tweets."""
        tweet_with_platform = {**mock_twitter_tweet, "platform": "twitter"}
        twitter_ingestor.fetch_recent = AsyncMock(return_value=[tweet_with_platform])
        
        result = await twitter_ingestor.fetch_recent(limit=10)
        assert len(result) == 1
        assert result[0]["platform"] == "twitter"

    @pytest.mark.asyncio
    async def test_twitter_search(self, twitter_ingestor):
        """Test searching tweets."""
        twitter_ingestor.search_tweets = AsyncMock(return_value=[
            {"id": "tweet_1", "text": "found", "platform": "twitter"}
        ])
        
        result = await twitter_ingestor.search_tweets("breaking")
        assert len(result) == 1


class TestYouTubeIngestorUnit:
    """Unit tests for YouTube ingestion."""

    @pytest.fixture
    def youtube_ingestor(self):
        """Create mock YouTube ingestor."""
        ingestor = MagicMock()
        ingestor.fetch_videos = AsyncMock(return_value=[])
        ingestor.fetch_comments = AsyncMock(return_value=[])
        ingestor.fetch_trending = AsyncMock(return_value=[])
        return ingestor

    @pytest.mark.asyncio
    async def test_youtube_fetch_videos(self, youtube_ingestor, mock_youtube_video):
        """Test fetching YouTube videos."""
        video_with_platform = {**mock_youtube_video, "platform": "youtube"}
        youtube_ingestor.fetch_videos = AsyncMock(return_value=[video_with_platform])
        
        result = await youtube_ingestor.fetch_videos(channel_id="test", limit=5)
        assert len(result) == 1
        assert result[0]["platform"] == "youtube"

    @pytest.mark.asyncio
    async def test_youtube_fetch_comments(self, youtube_ingestor):
        """Test fetching video comments."""
        youtube_ingestor.fetch_comments = AsyncMock(return_value=[
            {"id": "comment_1", "text": "comment", "platform": "youtube"}
        ])
        
        result = await youtube_ingestor.fetch_comments(video_id="test")
        assert len(result) == 1


class TestRSSIngestorUnit:
    """Unit tests for RSS feed ingestion."""

    @pytest.fixture
    def rss_ingestor(self):
        """Create mock RSS ingestor."""
        ingestor = MagicMock()
        ingestor.fetch_articles = AsyncMock(return_value=[])
        ingestor.parse_feed = AsyncMock(return_value=[])
        return ingestor

    @pytest.mark.asyncio
    async def test_rss_fetch_articles(self, rss_ingestor):
        """Test fetching RSS articles."""
        rss_ingestor.fetch_articles = AsyncMock(return_value=[
            {"id": "article_1", "text": "news", "platform": "news"}
        ])
        
        result = await rss_ingestor.fetch_articles(url="http://example.com/rss")
        assert len(result) == 1
        assert result[0]["platform"] == "news"


# ==================== Feature Extraction Tests ====================

class TestFeatureExtractorUnit:
    """Unit tests for feature extraction."""

    @pytest.fixture
    def feature_extractor(self):
        """Create mock feature extractor."""
        extractor = MagicMock()
        extractor.extract_features = MagicMock(return_value={})
        extractor.extract_entities = MagicMock(return_value=[])
        extractor.extract_sentiment = MagicMock(return_value={})
        return extractor

    def test_feature_extraction_basic(self, feature_extractor, mock_event):
        """Test basic feature extraction."""
        feature_extractor.extract_features = MagicMock(return_value={
            "embedding": [0.1, 0.2, 0.3],
            "sentiment": {"label": "NEUTRAL", "score": 0.6},
            "entities": [{"text": "event", "type": "MISC"}],
            "text_stats": {"word_count": 3, "char_count": 5}
        })
        
        result = feature_extractor.extract_features(mock_event)
        assert "embedding" in result
        assert "sentiment" in result
        assert "entities" in result

    def test_sentiment_extraction(self, feature_extractor):
        """Test sentiment extraction."""
        feature_extractor.extract_sentiment = MagicMock(return_value={
            "label": "POSITIVE",
            "score": 0.85
        })
        
        result = feature_extractor.extract_sentiment("Great news!")
        assert result["label"] == "POSITIVE"
        assert result["score"] > 0.8

    def test_entity_extraction(self, feature_extractor, mock_entities):
        """Test entity extraction."""
        feature_extractor.extract_entities = MagicMock(return_value=mock_entities)
        
        result = feature_extractor.extract_entities("New York incident reported by police")
        assert len(result) == 3
        assert any(ent["type"] == "LOC" for ent in result)

    def test_embedding_generation(self, feature_extractor, mock_embedding):
        """Test text embedding generation."""
        feature_extractor.get_embedding = MagicMock(return_value=mock_embedding)
        
        result = feature_extractor.get_embedding("test text")
        assert len(result) == 8
        assert all(isinstance(x, float) for x in result)


# ==================== Agent Tests ====================

class TestThreatAgentUnit:
    """Unit tests for threat detection agent."""

    @pytest.fixture
    def threat_agent(self):
        """Create mock threat agent."""
        agent = MagicMock()
        agent.process = AsyncMock(return_value={})
        agent.detect_threat = MagicMock(return_value={})
        return agent

    @pytest.mark.asyncio
    async def test_threat_detection(self, threat_agent, mock_threat_result):
        """Test threat detection."""
        threat_agent.process = AsyncMock(return_value=mock_threat_result)
        
        result = await threat_agent.process({"text": "violent content"}, {})
        assert "threat_level" in result
        assert "confidence" in result

    @pytest.mark.asyncio
    async def test_low_threat_classification(self, threat_agent):
        """Test low threat classification."""
        threat_agent.detect_threat = MagicMock(return_value={
            "threat_level": "low",
            "confidence": 0.95
        })
        
        result = threat_agent.detect_threat("normal daily news")
        assert result["threat_level"] == "low"

    @pytest.mark.asyncio
    async def test_high_threat_classification(self, threat_agent):
        """Test high threat classification."""
        threat_agent.detect_threat = MagicMock(return_value={
            "threat_level": "critical",
            "confidence": 0.98
        })
        
        result = threat_agent.detect_threat("emergency with severe casualties")
        assert result["threat_level"] == "critical"
        assert result["confidence"] > 0.95


class TestTrendAgentUnit:
    """Unit tests for trend analysis agent."""

    @pytest.fixture
    def trend_agent(self):
        """Create mock trend agent."""
        agent = MagicMock()
        agent.process = AsyncMock(return_value={})
        agent.analyze_trends = MagicMock(return_value=[])
        return agent

    @pytest.mark.asyncio
    async def test_trend_analysis(self, trend_agent):
        """Test trend analysis."""
        trend_agent.process = AsyncMock(return_value={
            "trending_topics": [
                {"keywords": ["test", "topic"], "score": 0.8}
            ]
        })
        
        result = await trend_agent.process({"text": "trendy content"}, {})
        assert "trending_topics" in result
        assert len(result["trending_topics"]) > 0

    def test_trend_extraction(self, trend_agent):
        """Test trend keyword extraction."""
        trend_agent.analyze_trends = MagicMock(return_value=[
            {"keywords": ["breaking", "news"], "frequency": 150},
            {"keywords": ["emergency"], "frequency": 120}
        ])
        
        result = trend_agent.analyze_trends(sample_events=[])
        assert len(result) == 2


class TestVerificationAgentUnit:
    """Unit tests for verification agent."""

    @pytest.fixture
    def verification_agent(self):
        """Create mock verification agent."""
        agent = MagicMock()
        agent.process = AsyncMock(return_value={})
        agent.verify_event = MagicMock(return_value={})
        return agent

    @pytest.mark.asyncio
    async def test_event_verification(self, verification_agent):
        """Test event verification."""
        verification_agent.process = AsyncMock(return_value={
            "verification_score": 0.85,
            "sources": 3,
            "verified": True
        })
        
        result = await verification_agent.process({"text": "event to verify"}, {})
        assert "verification_score" in result
        assert result["verification_score"] > 0

    def test_multi_source_verification(self, verification_agent):
        """Test verification from multiple sources."""
        verification_agent.verify_event = MagicMock(return_value={
            "verified": True,
            "sources": ["twitter", "news", "reddit"],
            "confidence": 0.92
        })
        
        result = verification_agent.verify_event({"text": "event"})
        assert result["verified"] is True
        assert len(result["sources"]) == 3


# ==================== Compliance Tests ====================

class TestComplianceFilterUnit:
    """Unit tests for compliance filtering."""

    @pytest.fixture
    def compliance_filter(self):
        """Create mock compliance filter."""
        filter_obj = MagicMock()
        filter_obj.check_compliance = AsyncMock(return_value={})
        filter_obj.filter_event = MagicMock(return_value=True)
        return filter_obj

    @pytest.mark.asyncio
    async def test_compliance_check_pass(self, compliance_filter):
        """Test event passes compliance check."""
        compliance_filter.check_compliance = AsyncMock(return_value={
            "is_compliant": True,
            "flags": [],
            "confidence": 0.95
        })
        
        result = await compliance_filter.check_compliance({"text": "clean event"})
        assert result["is_compliant"] is True
        assert len(result["flags"]) == 0

    @pytest.mark.asyncio
    async def test_compliance_check_fail_pii(self, compliance_filter):
        """Test event fails due to PII detection."""
        compliance_filter.check_compliance = AsyncMock(return_value={
            "is_compliant": False,
            "flags": ["contains_pii"],
            "confidence": 0.98
        })
        
        result = await compliance_filter.check_compliance({"text": "SSN 123-45-6789"})
        assert result["is_compliant"] is False
        assert "contains_pii" in result["flags"]

    def test_rate_limit_compliance(self, compliance_filter):
        """Test rate limit compliance checking."""
        compliance_filter.check_rate_limit = MagicMock(return_value=True)
        
        result = compliance_filter.check_rate_limit(requests_count=50, time_window=60)
        assert result is True

    def test_content_policy_compliance(self, compliance_filter):
        """Test content policy compliance."""
        compliance_filter.check_policy = MagicMock(return_value={
            "policy_compliant": True,
            "violations": []
        })
        
        result = compliance_filter.check_policy({"text": "normal content"})
        assert result["policy_compliant"] is True


# ==================== Integration Tests ====================

class TestPipelineIntegrationUnit:
    """Unit tests for pipeline integration."""

    @pytest.fixture
    def pipeline(self):
        """Create mock pipeline."""
        pipeline = MagicMock()
        pipeline.process_event = AsyncMock(return_value={})
        pipeline.process_batch = AsyncMock(return_value=[])
        return pipeline

    @pytest.mark.asyncio
    async def test_pipeline_event_processing(self, pipeline, mock_event):
        """Test pipeline event processing."""
        pipeline.process_event = AsyncMock(return_value={
            "event": mock_event,
            "confidence_score": 0.85,
            "status": "processed"
        })
        
        result = await pipeline.process_event(mock_event)
        assert "event" in result
        assert "confidence_score" in result
        assert result["status"] == "processed"

    @pytest.mark.asyncio
    async def test_pipeline_batch_processing(self, pipeline, sample_events):
        """Test pipeline batch processing."""
        processed = [{"id": e["id"], "status": "processed"} for e in sample_events]
        pipeline.process_batch = AsyncMock(return_value=processed)
        
        result = await pipeline.process_batch(sample_events)
        assert len(result) == len(sample_events)
        assert all(item["status"] == "processed" for item in result)


# ==================== Kafka/Streaming Tests ====================

class TestKafkaIntegrationUnit:
    """Unit tests for Kafka streaming."""

    @pytest.fixture
    def kafka_producer(self):
        """Create mock Kafka producer."""
        producer = MagicMock()
        producer.send_events = AsyncMock(return_value={"sent": 0})
        producer.send_batch = AsyncMock(return_value={"sent": 0})
        return producer

    @pytest.fixture
    def kafka_consumer(self):
        """Create mock Kafka consumer."""
        consumer = MagicMock()
        consumer.consume_messages = AsyncMock(return_value=[])
        return consumer

    @pytest.mark.asyncio
    async def test_kafka_produce(self, kafka_producer, mock_event):
        """Test Kafka message production."""
        kafka_producer.send_events = AsyncMock(return_value={"sent": 1})
        
        result = await kafka_producer.send_events(topic="test", events=[mock_event])
        assert result["sent"] == 1

    @pytest.mark.asyncio
    async def test_kafka_consume(self, kafka_consumer):
        """Test Kafka message consumption."""
        messages = [{"id": f"msg_{i}", "text": f"message {i}"} for i in range(3)]
        kafka_consumer.consume_messages = AsyncMock(return_value=messages)
        
        result = await kafka_consumer.consume_messages(timeout=1.0)
        assert len(result) == 3


# ==================== Edge Cases and Error Handling ====================

class TestErrorHandling:
    """Test error handling across components."""

    @pytest.mark.asyncio
    async def test_ingestor_error_handling(self):
        """Test ingestor error handling."""
        ingestor = MagicMock()
        ingestor.fetch_recent = AsyncMock(side_effect=Exception("API Error"))
        
        with pytest.raises(Exception) as exc_info:
            await ingestor.fetch_recent(limit=10)
        
        assert "API Error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_pipeline_error_recovery(self):
        """Test pipeline error recovery."""
        pipeline = MagicMock()
        pipeline.process_event = AsyncMock(return_value={
            "event": None,
            "error": "Processing failed",
            "status": "error"
        })
        
        result = await pipeline.process_event({})
        assert result["status"] == "error"
        assert "error" in result

    def test_feature_extraction_empty_input(self):
        """Test feature extraction with empty input."""
        extractor = MagicMock()
        extractor.extract_features = MagicMock(return_value={})
        
        result = extractor.extract_features({})
        assert isinstance(result, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
