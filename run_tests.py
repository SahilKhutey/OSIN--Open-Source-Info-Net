#!/usr/bin/env python3
"""
OSIN Test Runner
Run pytest tests directly from Python without shell dependencies.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_tests():
    """Run the OSIN test suite."""
    
    os.chdir(r"C:\Users\User\Documents\OSIN")
    
    print("=" * 70)
    print("OSIN Test Suite Runner")
    print("=" * 70)
    
    # Check if pytest is available
    print("\n1. Checking pytest installation...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--version"],
            capture_output=True,
            text=True,
            timeout=30
        )
        print(result.stdout)
        if result.returncode != 0:
            print("⚠️  pytest not found. Install with: pip install pytest")
            return False
    except Exception as e:
        print(f"❌ Error checking pytest: {e}")
        return False
    
    # Run unit tests
    print("\n2. Running unit tests...")
    print("-" * 70)
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", 
             "backend/tests/test_core_units.py", 
             "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=120
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        unit_passed = result.returncode == 0
        print(f"\n✓ Unit tests: {'PASSED' if unit_passed else 'FAILED'}")
    except subprocess.TimeoutExpired:
        print("❌ Unit tests timed out")
        unit_passed = False
    except Exception as e:
        print(f"❌ Error running unit tests: {e}")
        unit_passed = False
    
    # Run integration tests
    print("\n3. Running integration tests...")
    print("-" * 70)
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", 
             "backend/tests/test_integration_system.py", 
             "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=120
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        integration_passed = result.returncode == 0
        print(f"\n✓ Integration tests: {'PASSED' if integration_passed else 'FAILED'}")
    except subprocess.TimeoutExpired:
        print("❌ Integration tests timed out")
        integration_passed = False
    except Exception as e:
        print(f"❌ Error running integration tests: {e}")
        integration_passed = False
    
    # Run AI/Load tests
    print("\n4. Running AI/Load tests...")
    print("-" * 70)
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", 
             "backend/tests/test_ai_load.py", 
             "-v", "--tb=short", "-m", "ai"],
            capture_output=True,
            text=True,
            timeout=120
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        ai_passed = result.returncode == 0
        print(f"\n✓ AI tests: {'PASSED' if ai_passed else 'FAILED'}")
    except subprocess.TimeoutExpired:
        print("❌ AI tests timed out")
        ai_passed = False
    except Exception as e:
        print(f"❌ Error running AI tests: {e}")
        ai_passed = False
    
    # Generate coverage report
    print("\n5. Generating coverage report...")
    print("-" * 70)
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", 
             "backend/tests/",
             "--cov=backend/app", "--cov-report=term",
             "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=180
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        coverage_generated = result.returncode == 0
        print(f"\n✓ Coverage report: {'GENERATED' if coverage_generated else 'FAILED'}")
    except subprocess.TimeoutExpired:
        print("❌ Coverage report generation timed out")
        coverage_generated = False
    except Exception as e:
        print(f"❌ Error generating coverage: {e}")
        coverage_generated = False
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUITE SUMMARY")
    print("=" * 70)
    
    results = {
        "Unit Tests": unit_passed,
        "Integration Tests": integration_passed,
        "AI/Load Tests": ai_passed,
        "Coverage Report": coverage_generated
    }
    
    for name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name:.<50} {status}")
    
    all_passed = all(results.values())
    print("=" * 70)
    
    if all_passed:
        print("🎉 ALL TESTS PASSED! 🎉")
        print("\nNext steps:")
        print("- Review test results above")
        print("- Check htmlcov/index.html for detailed coverage")
        print("- Read QUICK_START.md for more commands")
        return True
    else:
        print("⚠️  Some tests failed. Review output above.")
        return False

if __name__ == "__main__":
    try:
        success = run_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Test run interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
