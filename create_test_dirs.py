#!/usr/bin/env python3
"""Create test directory structure for OSIN."""

import os
from pathlib import Path

# List of all directories to create
directories = [
    "backend/tests/unit/ingestion/social",
    "backend/tests/unit/features",
    "backend/tests/unit/agents",
    "backend/tests/unit/compliance",
    "backend/tests/integration/pipeline",
    "backend/tests/integration/kafka",
    "backend/tests/integration/ai",
    "backend/tests/streaming",
    "backend/tests/ai",
    "backend/tests/system",
    "backend/tests/ui",
    "backend/tests/load"
]

base_path = Path("C:\\Users\\User\\Documents\\OSIN")
os.chdir(base_path)

# Create each directory and __init__.py
for dir_path in directories:
    # Convert forward slashes to backslashes for Windows
    dir_full_path = Path(dir_path)
    dir_full_path.mkdir(parents=True, exist_ok=True)
    
    # Create __init__.py with a simple comment
    init_file = dir_full_path / "__init__.py"
    init_file.write_text("# Test module for OSIN\n")
    
    print(f"Created: {dir_path} with __init__.py")

print("\nAll test directories created successfully!")
