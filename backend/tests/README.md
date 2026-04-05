# OSIN Comprehensive Test Suite

A complete testing architecture for the OSIN Intelligence Ingestion System covering unit tests, integration tests, streaming validation, AI verification, system tests, UI tests, and load testing.

## 📁 Directory Structure

```
backend/tests/
├── conftest.py                 # Global test fixtures and configuration
├── pytest.ini                  # Pytest configuration
├── requirements-test.txt       # Test dependencies
│
├── unit/                       # Unit tests (fast, isolated)
│   ├── ingestion/              # Ingestor unit tests
│   │   └── social/             # Social media platform tests
│   │       ├── test_reddit_ingest.py
│   │       ├── test_twitter_ingest.py
│   │       └── ...
│   ├── features/               # Feature extraction tests
│   │   └── test_feature_extractor.py
│   ├── agents/                 # AI agent unit tests
│   │   ├── test_threat_agent.py
│   │   ├── test_trend_agent.py
│   │   └── ...
│   └── compliance/             # Compliance filter tests
│       └── test_compliance_filter.py
│
├── integration/                # Integration tests
│   ├── pipeline/               # Pipeline integration tests
│   │   └── test_pipeline_integration.py
│   ├── kafka/                  # Kafka producer/consumer tests
│   │   └── test_kafka_integration.py
│   └── ai/                     # AI pipeline integration tests
│       └── test_ai_integration.py
│
├── streaming/                  # Streaming/Kafka tests
│   ├── test_kafka_integration.py
│   └── test_realtime_validation.py
│
├── ai/                         # AI/ML validation tests
│   ├── test_nlp_validation.py
│   ├── test_threat_detection.py
│   └── test_verification.py
│
├── system/                     # System/E2E tests
│   ├── test_full_pipeline.py
│   └── test_e2e_workflows.py
│
├── ui/                         # UI/Playwright tests
│   ├── test_dashboard.py
│   └── test_terminal.py
│
└── load/                       # Load/stress testing
    ├── locustfile.py
    └── test_stress.py
```

## 🚀 Quick Start

### 1. Install Test Dependencies

```bash
# Install from requirements-test.txt
pip install -r backend/tests/requirements-test.txt

# Or individually
pip install pytest pytest-asyncio pytest-cov playwright locust
```

### 2. Setup Test Infrastructure

```bash
# Create test directory structure
python bootstrap_tests.py

# Install Playwright browsers (for UI tests)
python -m playwright install
```

### 3. Run Tests

```bash
# Run all tests
pytest backend/tests/ -v

# Run specific test suite
pytest backend/tests/unit/ -v                    # Unit tests only
pytest backend/tests/integration/ -v             # Integration tests only
pytest backend/tests/ -m unit                   # Using markers
pytest backend/tests/ -m "not slow"             # Exclude slow tests

# Run with coverage
pytest backend/tests/ --cov=backend/app --cov-report=html

# Run specific test file
pytest backend/tests/unit/ingestion/social/test_reddit_ingest.py -v
```

## 🧪 Test Categories

### Unit Tests (`tests/unit/`)
- **Purpose**: Test individual components in isolation
- **Speed**: Very fast (<1ms per test)
- **Fixtures**: Comprehensive mocks for all external dependencies
- **Coverage Target**: >90% per module

**Includes:**
- Ingestor unit tests (Reddit, Twitter, YouTube, RSS, etc.)
- Feature extraction tests
- Agent unit tests (Threat, Trend, Verification)
- Compliance filter tests

### Integration Tests (`tests/integration/`)
- **Purpose**: Test component interactions and pipelines
- **Speed**: Moderate (10-100ms per test)
- **Fixtures**: Mocked services, test databases
- **Focus**: Data flow between components

**Includes:**
- Full pipeline processing tests
- Kafka producer/consumer integration
- AI agent coordination tests
- Cross-component data validation

### Streaming Tests (`tests/streaming/`)
- **Purpose**: Validate Kafka integration and real-time processing
- **Requirements**: Kafka/Redpanda running
- **Fixtures**: Mock Kafka brokers, message producers/consumers
- **Focus**: Message serialization, delivery guarantees

### AI/ML Tests (`tests/ai/`)
- **Purpose**: Validate NLP models and AI verification
- **Fixtures**: Mock ML models, test embeddings
- **Focus**: Model predictions, entity extraction, sentiment analysis

### System Tests (`tests/system/`)
- **Purpose**: End-to-end workflow validation
- **Speed**: Slower (100ms - 5s per test)
- **Scope**: Complete workflows from ingestion to intelligence output
- **Focus**: Error handling, resilience, data consistency

### UI Tests (`tests/ui/`)
- **Purpose**: Browser automation testing with Playwright
- **Technology**: Playwright (Chrome, Firefox, Webkit)
- **Focus**: Dashboard functionality, terminal interface, real-time updates
- **Markers**: `@pytest.mark.ui`

### Load Tests (`tests/load/`)
- **Purpose**: Performance and stress testing
- **Tool**: Locust for distributed load generation
- **Focus**: Throughput, latency, resource usage
- **Markers**: `@pytest.mark.load`

## 📊 Coverage Goals

- **Overall**: >80% code coverage
- **Critical Paths**: >95% coverage
- **Unit Tests**: >90% per module
- **Integration**: >70% per pipeline

## 🔧 Fixtures Reference

### Common Fixtures (from `conftest.py`)

```python
# Event fixtures
@pytest.fixture
def mock_event()              # Standardized test event
def sample_events()           # Multiple events

# Social media fixtures
@pytest.fixture
def mock_reddit_submission()  # Mock Reddit submission
def mock_twitter_tweet()      # Mock Twitter tweet
def mock_youtube_video()      # Mock YouTube video metadata

# Feature/AI fixtures
@pytest.fixture
def mock_embedding()          # Text embedding vector
def mock_entities()           # Extracted entities
def mock_sentiment()          # Sentiment analysis result
def mock_threat_result()      # Threat detection result

# Pipeline fixtures
@pytest.fixture
def mock_normalized_event()   # Normalized event
def mock_feature_extracted_event()  # Event with features
def mock_verified_event()     # Verified event

# Kafka fixtures
@pytest.fixture
def mock_kafka_message()      # Single Kafka message
def mock_kafka_messages_batch()  # Batch of messages

# Manager fixtures
@pytest.fixture
def mock_ingestor()           # Mock ingestor
def mock_pipeline()           # Mock pipeline
def mock_kafka_producer()     # Mock Kafka producer
def mock_kafka_consumer()     # Mock Kafka consumer
```

### Custom Fixtures

Create custom fixtures in individual test files:

```python
@pytest.fixture
def my_custom_fixture():
    """My custom fixture."""
    return {
        "data": "value",
        "nested": {"key": "value"}
    }
```

## 🏃 Running Specific Tests

```bash
# Run tests with specific marker
pytest -m unit                 # Unit tests only
pytest -m integration         # Integration tests only
pytest -m "not slow"          # Exclude slow tests
pytest -m "requires_kafka"    # Tests requiring Kafka

# Run tests for specific module
pytest backend/tests/unit/ingestion/social/ -v

# Run single test file
pytest backend/tests/unit/ingestion/social/test_reddit_ingest.py -v

# Run single test class
pytest backend/tests/unit/ingestion/social/test_reddit_ingest.py::TestRedditIngestor -v

# Run single test method
pytest backend/tests/unit/ingestion/social/test_reddit_ingest.py::TestRedditIngestor::test_fetch_recent_success -v

# Run with output
pytest -v -s                  # Verbose + print statements
pytest -x                     # Stop on first failure
pytest --lf                   # Run last failed tests
pytest --ff                   # Failed tests first
```

## 📈 Coverage Reporting

```bash
# Generate HTML coverage report
pytest --cov=backend/app --cov-report=html backend/tests/

# View specific module coverage
pytest --cov=backend/app/ingestion --cov-report=term backend/tests/unit/ingestion/

# Coverage with branch coverage
pytest --cov=backend/app --cov-branch --cov-report=html backend/tests/
```

Reports are generated in `htmlcov/` directory.

## 🔍 Test Markers

Defined in `pytest.ini`:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.streaming` - Streaming/Kafka tests
- `@pytest.mark.ai` - AI validation tests
- `@pytest.mark.system` - System/E2E tests
- `@pytest.mark.ui` - UI/Playwright tests
- `@pytest.mark.load` - Load tests
- `@pytest.mark.slow` - Long-running tests
- `@pytest.mark.requires_kafka` - Requires Kafka running
- `@pytest.mark.requires_external_api` - Requires external services

## 🐛 Debugging Tests

```bash
# Run with verbose output
pytest -vv backend/tests/

# Show print statements
pytest -s backend/tests/

# Drop into debugger on failure
pytest --pdb backend/tests/

# Detailed traceback
pytest --tb=long backend/tests/

# Show local variables on failure
pytest -l backend/tests/
```

## 📝 Writing Tests

### Basic Test Structure

```python
import pytest
from unittest.mock import MagicMock, AsyncMock

pytestmark = pytest.mark.unit

class TestMyComponent:
    """Test cases for MyComponent."""
    
    @pytest.fixture
    def my_component(self):
        """Create component for testing."""
        return MyComponent()
    
    def test_basic_functionality(self, my_component):
        """Test basic functionality."""
        result = my_component.do_something()
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_async_method(self, my_component):
        """Test async method."""
        result = await my_component.async_method()
        assert result == expected_value
```

### Using Mocks

```python
from unittest.mock import MagicMock, AsyncMock, patch

# Mock instance method
component.method = MagicMock(return_value=42)

# Mock async method
component.async_method = AsyncMock(return_value={"status": "ok"})

# Mock with side effect (multiple calls)
component.fetch = AsyncMock(side_effect=[
    [1, 2, 3],
    [4, 5, 6],
    []
])

# Verify calls
component.method.assert_called_once()
component.method.assert_called_with(arg1, arg2)
component.method.assert_called_once_with(arg1, arg2)

# Patch module
with patch('module.function') as mock_func:
    mock_func.return_value = test_value
```

## 🚀 CI/CD Integration

Tests are automatically run on:
- Push to `main` branch
- Push to `develop` branch
- All pull requests

See `.github/workflows/test.yml` for CI/CD configuration.

## 🤝 Contributing Tests

When adding new features:

1. Write unit tests first (TDD approach)
2. Ensure >80% coverage
3. Add integration tests for component interactions
4. Update this README with new test categories
5. Run full test suite before submitting PR

## 📚 Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [unittest.mock documentation](https://docs.python.org/3/library/unittest.mock.html)
- [Playwright Python documentation](https://playwright.dev/python/)
- [Locust documentation](https://locust.io/)

## ✅ Checklist for Test Completeness

- [ ] Unit tests written with >90% coverage
- [ ] Integration tests verify component interactions
- [ ] Fixtures cover all major scenarios
- [ ] Error cases and edge cases tested
- [ ] Async/await patterns properly tested
- [ ] Mock objects properly configured
- [ ] Tests are deterministic (not flaky)
- [ ] Test names clearly describe what they test
- [ ] Coverage report generated and reviewed
- [ ] All tests pass before committing

---

**Last Updated**: 2024
**Status**: Foundation Phase Complete ✓
