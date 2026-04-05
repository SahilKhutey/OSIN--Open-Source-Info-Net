#!/usr/bin/env python3
"""Setup test directory structure."""

import os
import sys
from pathlib import Path

# Change to script directory
os.chdir(Path(__file__).parent)

# Base test directory
base_path = Path("backend/tests")

# Directory structure to create
dirs = [
    "unit/ingestion/social",
    "unit/features",
    "unit/agents",
    "unit/compliance",
    "integration/pipeline",
    "integration/kafka",
    "integration/ai",
    "streaming",
    "ai",
    "system",
    "ui",
    "load",
]

# Create all directories
count = 0
for dir_path in dirs:
    full_path = base_path / dir_path
    full_path.mkdir(parents=True, exist_ok=True)
    
    # Create __init__.py for each directory and all parent directories
    init_file = full_path / "__init__.py"
    init_file.write_text("# Test module for OSIN\n")
    count += 1
    
    print(f"✓ Created {full_path} with __init__.py")
    
    # Also create __init__.py for parent directories if they don't exist
    parent = full_path.parent
    while parent != base_path and parent != base_path.parent:
        parent_init = parent / "__init__.py"
        if not parent_init.exists():
            parent_init.write_text("# Test module for OSIN\n")
            print(f"✓ Created {parent}/__init__.py")
        parent = parent.parent

# Create __init__.py for base directories that might be missing
for parent_dir in ["unit", "integration"]:
    parent_init = base_path / parent_dir / "__init__.py"
    if not parent_init.exists():
        parent_init.write_text("# Test module for OSIN\n")
        print(f"✓ Created {base_path / parent_dir}/__init__.py")

print(f"\n✓ Test directory structure created successfully!")
print(f"✓ Created {count} test directories")
sys.exit(0)
