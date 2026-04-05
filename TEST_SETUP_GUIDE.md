# OSIN Test Directory Structure Setup

## Quick Start

To create the test directory structure, run ONE of these commands from the OSIN directory:

### Option 1: Run Python script directly (recommended)
```bash
python create_test_structure.py
```

### Option 2: Use batch file wrapper (Windows)
Double-click: `setup_tests_run.bat`

### Option 3: Use existing setup script
```bash
python setup_tests.py
```

## Directory Structure to be Created

Once executed, the following directory structure will be created:

```
backend/tests/
├── __init__.py (already exists)
├── unit/
│   ├── __init__.py
│   ├── ingestion/
│   │   ├── __init__.py
│   │   └── social/
│   │       └── __init__.py
│   ├── features/
│   │   └── __init__.py
│   ├── agents/
│   │   └── __init__.py
│   └── compliance/
│       └── __init__.py
├── integration/
│   ├── __init__.py
│   ├── pipeline/
│   │   └── __init__.py
│   ├── kafka/
│   │   └── __init__.py
│   └── ai/
│       └── __init__.py
├── streaming/
│   └── __init__.py
├── ai/
│   └── __init__.py
├── system/
│   └── __init__.py
├── ui/
│   └── __init__.py
└── load/
    └── __init__.py
```

## Directory Details

The following 12 main test directories will be created:

1. **backend/tests/unit/ingestion/social/** - Social media ingestion unit tests
2. **backend/tests/unit/features/** - Feature-specific unit tests
3. **backend/tests/unit/agents/** - Agent-related unit tests
4. **backend/tests/unit/compliance/** - Compliance unit tests
5. **backend/tests/integration/pipeline/** - Data pipeline integration tests
6. **backend/tests/integration/kafka/** - Kafka integration tests
7. **backend/tests/integration/ai/** - AI service integration tests
8. **backend/tests/streaming/** - Streaming functionality tests
9. **backend/tests/ai/** - AI module tests
10. **backend/tests/system/** - System-level tests
11. **backend/tests/ui/** - UI tests
12. **backend/tests/load/** - Load testing

## Contents of __init__.py Files

Each `__init__.py` file will contain:

```python
# Test module for OSIN
```

This makes each directory a valid Python package that can be imported.

## Files Available for Execution

- **create_test_structure.py** - Main Python script (fully functional)
- **setup_tests_run.bat** - Batch file wrapper for easy execution
- **setup_tests.py** - Original setup script (also works)
- **create_dirs.py** - Alternative Python script

## Verification

After running the script, verify the structure was created:

```bash
# List all test directories
dir /s backend\tests

# Verify __init__.py files exist
find backend\tests -name "__init__.py"
```

## Notes

- All directories will be created with parent directories automatically
- Existing directories and files will not be overwritten
- The script is idempotent - safe to run multiple times
- Each __init__.py file is a Python module initialization file
