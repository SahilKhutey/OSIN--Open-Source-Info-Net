#!/usr/bin/env python3
"""Start OSIN Backend Server"""
import subprocess
import sys
import os
import time

# Change to backend directory
os.chdir(os.path.join(os.path.dirname(__file__), 'backend'))

# Start the server
cmd = [
    sys.executable, '-m', 'uvicorn',
    'app.main:app',
    '--host', '0.0.0.0',
    '--port', '8000',
    '--reload'
]

print("Starting OSIN Backend Server...")
print(f"Command: {' '.join(cmd)}")
print(f"Working directory: {os.getcwd()}")
print("-" * 60)

try:
    subprocess.run(cmd)
except KeyboardInterrupt:
    print("\nServer stopped.")
    sys.exit(0)
