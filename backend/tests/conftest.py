"""
Pytest configuration and fixtures for OSIN test suite.
Provides common fixtures, mocks, and test utilities across all test modules.
"""

import pytest
import asyncio
import os
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta

# Configure test environment
os.environ["TESTING"] = "true"
os.environ["KAFKA_BOOTSTRAP_SERVERS"] = "localhost:9092"
os.environ["COMPLIANCE_MODE"] = "test"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ==================== Common Test Fixtures ====================

@pytest.fixture
def mock_event():
    """Provide a standardized test event."""
    return {
        "id": "test_event_1",
        "platform": "test",
        "text": "Test event content for validation",
        "timestamp": datetime.utcnow().isoformat(),
        "engagement": 100,
        "confidence": 0.8
    }


@pytest.fixture
def mock_alert():
    """Provide a standardized test alert."""
    return {
        "id": "test_alert_1",
        "priority": "high",
        "message": "Test alert message",
        "timestamp": datetime.utcnow().isoformat(),
        "acknowledged": False
    }


@pytest.fixture
def sample_events():
    """Provide multiple sample events for testing."""
    return [
        {
            "id": f"event_{i}",
            "platform": ["twitter", "reddit", "news"][i % 3],
            "text": f"Sample event {i} with important content",
            "timestamp": (datetime.utcnow() - timedelta(minutes=i)).isoformat(),
            "engagement": i * 10,
            "confidence": 0.7 + (i * 0.05) if i * 0.05 <= 0.3 else 1.0
        }
        for i in range(10)
    ]


@pytest.fixture
def mock_raw_event():
    """Provide a raw unprocessed event."""
    return {
        "id": "raw_test_1",
        "platform": "twitter",
        "text": "Raw unprocessed event with noise and formatting",
        "timestamp": datetime.utcnow().isoformat(),
        "engagement": 150,
        "author": "test_user",
        "url": "https://twitter.com/test/status/123456"
    }


# ==================== Social Media Fixtures ====================

@pytest.fixture
def mock_reddit_submission():
    """Provide a mock Reddit submission object."""
    submission = MagicMock()
    submission.id = "test123"
    submission.title = "Test Post"
    submission.selftext = "Test content"
    submission.author = MagicMock()
    submission.author.__str__ = lambda x: "test_user"
    submission.permalink = "/r/test/comments/test123/"
    submission.created_utc = datetime.utcnow().timestamp()
    submission.score = 100
    submission.num_comments = 25
    submission.all_awardings = []
    submission.over_18 = False
    submission.removed_by_category = None
    submission.link_flair_text = None
    submission.domain = "self.test"
    submission.subreddit = MagicMock()
    submission.subreddit.display_name = "test"
    return submission


@pytest.fixture
def mock_twitter_tweet():
    """Provide a mock Twitter tweet object."""
    tweet = {
        "id": "tweet_123",
        "text": "Test tweet content",
        "author_id": "user_456",
        "created_at": datetime.utcnow().isoformat(),
        "public_metrics": {
            "retweet_count": 50,
            "reply_count": 25,
            "like_count": 200,
            "quote_count": 10
        },
        "lang": "en"
    }
    return tweet


@pytest.fixture
def mock_youtube_video():
    """Provide a mock YouTube video metadata."""
    return {
        "id": "dQw4w9WgXcQ",
        "title": "Test Video Title",
        "channel_id": "test_channel_123",
        "published_at": datetime.utcnow().isoformat(),
        "description": "Test video description with content",
        "view_count": 1000,
        "like_count": 100,
        "comment_count": 50,
        "duration": "PT5M30S",
        "tags": ["test", "news", "breaking"]
    }


# ==================== Feature & AI Fixtures ====================

@pytest.fixture
def mock_embedding():
    """Provide a mock text embedding vector."""
    return [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]


@pytest.fixture
def mock_entities():
    """Provide mock extracted entities."""
    return [
        {"text": "New York", "type": "LOC", "confidence": 0.95},
        {"text": "incident", "type": "EVENT", "confidence": 0.88},
        {"text": "police", "type": "ORG", "confidence": 0.92}
    ]


@pytest.fixture
def mock_sentiment():
    """Provide mock sentiment analysis result."""
    return {
        "label": "NEGATIVE",
        "score": 0.85
    }


@pytest.fixture
def mock_threat_result():
    """Provide a mock threat detection result."""
    return {
        "threat_level": "violence",
        "confidence": 0.82,
        "details": {
            "method": "ai_classification",
            "keywords": ["violence", "attack"],
            "context": "Breaking news alert"
        }
    }


# ==================== Pipeline Fixtures ====================

@pytest.fixture
def mock_normalized_event():
    """Provide a normalized event after preprocessing."""
    return {
        "id": "normalized_test_1",
        "text": "Normalized event text without noise",
        "platform": "twitter",
        "normalized_timestamp": datetime.utcnow().isoformat(),
        "source_language": "en",
        "cleaned_text": "normalized event text without noise"
    }


@pytest.fixture
def mock_feature_extracted_event():
    """Provide an event with extracted features."""
    return {
        "id": "features_test_1",
        "text": "Event with features",
        "platform": "twitter",
        "embedding": [0.1, 0.2, 0.3, 0.4],
        "sentiment": {"label": "NEUTRAL", "score": 0.6},
        "entities": [{"text": "event", "type": "MISC", "confidence": 0.85}],
        "text_stats": {
            "word_count": 3,
            "char_count": 18,
            "has_urls": False,
            "has_mentions": False,
            "has_questions": False
        },
        "engagement_score": 0.5
    }


@pytest.fixture
def mock_verified_event():
    """Provide a verified event with confidence scores."""
    return {
        "event_id": "verified_test_1",
        "text": "Verified event content",
        "entities": [{"text": "event", "type": "MISC"}],
        "sentiment": "NEUTRAL",
        "verification": {
            "confidence": 0.85,
            "sources": 3,
            "similar_events": ["event_456", "event_789"]
        },
        "final_confidence": 0.88
    }


# ==================== Kafka/Streaming Fixtures ====================

@pytest.fixture
def mock_kafka_message():
    """Provide a mock Kafka message."""
    return {
        "id": "kafka_test_1",
        "text": "Kafka streamed event",
        "platform": "twitter",
        "timestamp": datetime.utcnow().isoformat()
    }


@pytest.fixture
def mock_kafka_messages_batch():
    """Provide multiple mock Kafka messages."""
    return [
        {
            "id": f"batch_event_{i}",
            "text": f"Batch event {i}",
            "platform": ["twitter", "reddit", "news"][i % 3],
            "timestamp": datetime.utcnow().isoformat()
        }
        for i in range(5)
    ]


# ==================== Compliance Fixtures ====================

@pytest.fixture
def mock_compliance_check_result():
    """Provide a mock compliance check result."""
    return {
        "is_compliant": True,
        "flags": [],
        "confidence": 0.95,
        "checks": {
            "rate_limit": True,
            "privacy": True,
            "content_policy": True,
            "data_retention": True
        }
    }


@pytest.fixture
def mock_non_compliant_event():
    """Provide an event that violates compliance rules."""
    return {
        "id": "non_compliant_1",
        "text": "PII data: John Smith SSN 123-45-6789",
        "platform": "twitter",
        "contains_pii": True,
        "contains_violence": True
    }


# ==================== API/Response Fixtures ====================

@pytest.fixture
def mock_api_response():
    """Provide a mock API response."""
    return {
        "status": "success",
        "data": [
            {"id": "1", "text": "Response item 1"},
            {"id": "2", "text": "Response item 2"}
        ],
        "count": 2,
        "timestamp": datetime.utcnow().isoformat()
    }


@pytest.fixture
def mock_error_response():
    """Provide a mock error response."""
    return {
        "status": "error",
        "error": "Invalid request",
        "message": "The request could not be processed",
        "code": 400
    }


# ==================== Mock Managers ====================

@pytest.fixture
def mock_ingestor():
    """Provide a mock ingestor with common methods."""
    ingestor = AsyncMock()
    ingestor.fetch_recent = AsyncMock(return_value=[])
    ingestor.fetch_by_query = AsyncMock(return_value=[])
    ingestor.health_check = AsyncMock(return_value={"status": "healthy"})
    return ingestor


@pytest.fixture
def mock_pipeline():
    """Provide a mock processing pipeline."""
    pipeline = AsyncMock()
    pipeline.process_event = AsyncMock(return_value={
        "event": {"id": "test", "text": "processed"},
        "confidence_score": 0.85
    })
    pipeline.process_batch = AsyncMock(return_value=[])
    return pipeline


@pytest.fixture
def mock_kafka_producer():
    """Provide a mock Kafka producer."""
    producer = MagicMock()
    producer.send_events = AsyncMock(return_value={"sent": 1})
    producer.health_check = AsyncMock(return_value={"status": "connected"})
    return producer


@pytest.fixture
def mock_kafka_consumer():
    """Provide a mock Kafka consumer."""
    consumer = MagicMock()
    consumer.consume_messages = AsyncMock(return_value=[])
    consumer.get_offset = AsyncMock(return_value=0)
    return consumer

# ==================== Utility Functions ====================

@pytest.fixture
def assert_valid_event():
    """Provide a function to validate event structure."""
    def validator(event, required_fields=None):
        if required_fields is None:
            required_fields = ["id", "platform", "text", "timestamp"]

        for field in required_fields:
            assert field in event, f"Missing required field: {field}"

        assert isinstance(event["id"], str)
        assert isinstance(event["platform"], str)
        assert isinstance(event["text"], str)
        assert isinstance(event["timestamp"], str)

        return True

    return validator


@pytest.fixture
def mock_context():
    """Provide a mock context object for agent processing."""
    return {
        "trend_agent": {
            "output": {
                "trending_topics": [
                    {"keywords": ["test", "news"], "score": 0.8}
                ]
            }
        },
        "threat_agent": {
            "output": {
                "threat_level": "low",
                "confidence": 0.6
            }
        },
        "verification_agent": {
            "output": {
                "verification_score": 0.7,
                "sources": 2
            }
        }
    }


# ==================== Test Utilities ====================

def create_sample_event(event_id, platform="test", text="Sample event",
                        engagement=100, confidence=0.8):
    """Factory function to create sample events with custom parameters."""
    return {
        "id": event_id,
        "platform": platform,
        "text": text,
        "timestamp": datetime.utcnow().isoformat(),
        "engagement": engagement,
        "confidence": confidence
    }


def create_sample_events_batch(count=5, platform="test"):
    """Factory function to create a batch of sample events."""
    return [
        create_sample_event(f"event_{i}", platform=platform, engagement=i*100)
        for i in range(count)
    ]
