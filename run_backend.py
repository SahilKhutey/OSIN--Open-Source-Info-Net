#!/usr/bin/env python
import subprocess
import sys
import os

os.chdir('/c/Users/User/Documents/OSIN/backend')
subprocess.run([
    sys.executable, '-m', 'uvicorn',
    'app.main:app',
    '--host', '0.0.0.0',
    '--port', '8000',
    '--reload'
])
