#!/usr/bin/env python3
"""
OSIN Test Suite Setup Bootstrap
This script creates the entire test directory structure and initial test files.
Run this from the OSIN project root: python bootstrap_tests.py
"""

import os
import sys
from pathlib import Path

def setup_test_directories_and_files():
    """Create test directory structure and initial test files."""
    
    root_dir = Path(__file__).parent
    tests_dir = root_dir / "backend" / "tests"
    
    # Ensure tests directory exists
    tests_dir.mkdir(parents=True, exist_ok=True)
    
    # Define all directories to create
    directories = [
        "unit",
        "unit/ingestion",
        "unit/ingestion/social",
        "unit/features",
        "unit/agents",
        "unit/compliance",
        "integration",
        "integration/pipeline",
        "integration/kafka",
        "integration/ai",
        "streaming",
        "ai",
        "system",
        "ui",
        "load",
    ]
    
    print("=" * 60)
    print("OSIN Test Suite Setup")
    print("=" * 60)
    print(f"\nRoot directory: {root_dir}")
    print(f"Tests directory: {tests_dir}\n")
    
    # Create directories
    print("Creating test directories...")
    for dir_path in directories:
        full_path = tests_dir / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py
        init_file = full_path / "__init__.py"
        dir_name = dir_path.split('/')[-1].replace('_', ' ').title()
        init_content = f'"""{dir_name} Tests"""\n'
        
        if not init_file.exists():
            init_file.write_text(init_content)
        
        status = "✓" if full_path.exists() else "✗"
        print(f"  {status} {dir_path}/")
    
    print("\n✓ Test directory structure created successfully!")
    
    # Print summary
    print("\n" + "=" * 60)
    print("Next Steps:")
    print("=" * 60)
    print("""
1. Install test dependencies:
   pip install -r backend/tests/requirements-test.txt

2. Verify installation:
   pytest --collect-only backend/tests/

3. Run tests:
   pytest backend/tests/unit/ -v
   pytest backend/tests/ -v --cov=backend/app

4. Run specific test suites:
   pytest backend/tests/unit/ -m unit
   pytest backend/tests/integration/ -m integration
   pytest backend/tests/ai/ -m ai
   
For more information, see backend/tests/README.md
""")
    print("=" * 60)

if __name__ == "__main__":
    try:
        setup_test_directories_and_files()
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error during setup: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
