"""
Direct directory and test file creation for OSIN test suite.
Run this file to set up the complete test directory structure.
"""

from pathlib import Path


def create_directory_structure():
    """Create all test directories and __init__.py files."""

    base_dir = Path(__file__).parent / "backend" / "tests"
    
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

    print(f"Creating test directories in: {base_dir}\n")

    for dir_path in directories:
        full_path = base_dir / dir_path
        full_path.mkdir(parents=True, exist_ok=True)

        # Create __init__.py
        init_file = full_path / "__init__.py"
        if not init_file.exists():
            init_file.write_text(
                f"# {dir_path.split('/')[-1].replace('_', ' ').title()}"
                f" Tests\n"
            )

        print(f"✓ {dir_path}/__init__.py")

    print("\n✓ Directory structure created successfully!")
    return True


if __name__ == "__main__":
    try:
        create_directory_structure()
        print("\n✓ Test setup complete!")
        sys.exit(0)
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)
