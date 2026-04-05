#!/usr/bin/env python3
"""
Simple dashboard starter without subprocess dependencies.
"""
import sys
import os

# Set working directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("""
╔══════════════════════════════════════════════════════════════╗
║                  OSIN DASHBOARD LAUNCHER                    ║
║           Global Intelligence Engine Dashboard              ║
╚══════════════════════════════════════════════════════════════╝

🚀 Starting OSIN Dashboard System...
""")

# Check Python version
if sys.version_info < (3, 9):
    print("❌ Python 3.9+ required")
    sys.exit(1)

print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")

# Check dependencies
try:
    import fastapi
    print(f"✓ FastAPI installed")
except ImportError:
    print("❌ FastAPI not installed. Run: pip install fastapi uvicorn")
    sys.exit(1)

try:
    import uvicorn
    print(f"✓ Uvicorn installed")
except ImportError:
    print("❌ Uvicorn not installed. Run: pip install uvicorn")
    sys.exit(1)

print("\n📡 FastAPI Backend Server Ready!")
print("   To start backend, run: python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
print("   (from the backend directory)")

print("\n🌐 Frontend Dashboard Ready!")
frontend_path = os.path.join(os.getcwd(), "frontend", "index.html")
if os.path.exists(frontend_path):
    print(f"   Open in browser: file:///{frontend_path}")
else:
    print(f"   Dashboard file: {frontend_path}")

print("""
╔══════════════════════════════════════════════════════════════╗
║                  DASHBOARD READY TO RUN!                    ║
╚══════════════════════════════════════════════════════════════╝

📊 DASHBOARD URLS (once started):
  • Frontend: file:///C:/Users/User/Documents/OSIN/frontend/index.html
  • API Docs: http://localhost:8000/docs
  • Health: http://localhost:8000/health

🔧 QUICK START:
  1. Terminal 1: cd backend && python -m uvicorn app.main:app --reload
  2. Terminal 2: Open frontend/index.html in browser

✅ System Status: READY FOR DEPLOYMENT
""")
