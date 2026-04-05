#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OSIN Dashboard Launcher
Launches the FastAPI backend server and opens the frontend dashboard in browser
"""

import subprocess
import time
import webbrowser
import os
import sys
from pathlib import Path

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def print_banner():
    """Print fancy startup banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                  OSIN DASHBOARD LAUNCHER                    ║
║           Global Intelligence Engine Dashboard              ║
╚══════════════════════════════════════════════════════════════╝

Initializing OSIN Dashboard System...
"""
    print(banner)

def check_environment():
    """Check Python version and requirements"""
    print("[OK] Checking environment...")

    # Check Python version
    if sys.version_info < (3, 9):
        print("[FAIL] Python 3.9+ required")
        sys.exit(1)
    print(f"  [OK] Python {sys.version_info.major}.{sys.version_info.minor}")

    # Check FastAPI
    try:
        import fastapi
        print(f"  [OK] FastAPI {fastapi.__version__}")
    except ImportError:
        print("[FAIL] FastAPI not installed. Run: pip install fastapi uvicorn")
        sys.exit(1)

    # Check Uvicorn
    try:
        import uvicorn
        print(f"  [OK] Uvicorn installed")
    except ImportError:
        print("[FAIL] Uvicorn not installed. Run: pip install uvicorn")
        sys.exit(1)

def start_backend_server():
    """Start FastAPI backend server"""
    print("\n[START] Starting FastAPI Backend Server...")

    backend_dir = Path(__file__).parent / "backend"

    # Start uvicorn server
    cmd = [
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload",
        "--log-level", "info"
    ]

    print(f"  Command: {' '.join(cmd)}")
    print(f"  Working directory: {backend_dir}")

    process = subprocess.Popen(
        cmd,
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )

    # Wait for server to start
    print("  [WAIT] Waiting for server to start (5 seconds)...")
    time.sleep(5)

    # Check if process is still running
    if process.poll() is not None:
        print("[FAIL] Backend server failed to start")
        return None

    print("  [OK] Backend server started on http://localhost:8000")
    return process

def open_dashboard():
    """Open dashboard in default browser"""
    print("\n[BROWSER] Opening Dashboard in Browser...")

    frontend_dir = Path(__file__).parent / "frontend"
    index_path = frontend_dir / "index.html"

    if not index_path.exists():
        print(f"[FAIL] Dashboard file not found: {index_path}")
        print("  Opening API instead...")
        webbrowser.open("http://localhost:8000")
    else:
        # Open local file
        file_url = f"file:///{index_path.as_posix()}"
        print(f"  Opening: {file_url}")
        webbrowser.open(file_url)

    print("\n[OK] Dashboard opened in your default browser!")

def print_startup_info():
    """Print useful startup information"""
    info = """
========================================================================
                       DASHBOARD NOW ACTIVE!
========================================================================

DASHBOARD URLS:
  * Frontend Dashboard: file:///C:/Users/User/Documents/OSIN/frontend/index.html
  * API Documentation: http://localhost:8000/docs
  * API Redoc: http://localhost:8000/redoc
  * Health Check: http://localhost:8000/health

API ENDPOINTS:
  * GET  /api/v1/signals        - Get intelligence signals
  * GET  /health                - Health check
  * POST /api/v1/threats        - Report threats

DASHBOARD FEATURES:
  [OK] Real-time Intelligence Feed
  [OK] Threat Level Monitoring
  [OK] Trend Analysis & Forecasting
  [OK] Credibility Breakdown
  [OK] Multi-Domain Intelligence Fusion
  [OK] Combat Readiness Scoring
  [OK] Action Console

CONFIGURATION:
  * Backend: http://0.0.0.0:8000
  * Reload on changes: ENABLED
  * Log Level: INFO

TO STOP:
  Press Ctrl+C in the terminal

TO RESTART:
  1. Stop the current process (Ctrl+C)
  2. Run: python launch_dashboards.py

TIPS:
  * Check browser console (F12) for any client-side errors
  * Backend logs appear in the terminal below
  * Use API docs at http://localhost:8000/docs to test endpoints

========================================================================
       System is LIVE and ready for global intelligence operations
========================================================================
"""
    print(info)

def main():
    """Main launcher"""
    print_banner()

    # Check environment
    check_environment()

    # Start backend
    backend_process = start_backend_server()
    if not backend_process:
        print("\n[FAIL] Failed to start backend server")
        sys.exit(1)

    # Open dashboard
    open_dashboard()

    # Print startup info
    print_startup_info()

    # Keep the process running
    try:
        backend_process.wait()
    except KeyboardInterrupt:
        print("\n\n[STOP] Shutting down...")
        backend_process.terminate()
        backend_process.wait(timeout=5)
        print("[OK] Shutdown complete")

if __name__ == "__main__":
    main()
