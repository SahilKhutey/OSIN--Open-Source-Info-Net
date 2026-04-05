@echo off
REM OSIN Dashboard Launcher for Windows

echo.
echo ================================================================
echo                 OSIN DASHBOARD LAUNCHER
echo          Global Intelligence Engine Dashboard
echo ================================================================
echo.
echo Starting OSIN Dashboard System...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org
    pause
    exit /b 1
)

echo [OK] Python detected
echo.

REM Check if we're in the right directory
if not exist "backend\app\main.py" (
    echo Error: backend\app\main.py not found
    echo Please run this script from the OSIN project root directory
    pause
    exit /b 1
)

echo [OK] Project structure verified
echo.

REM Try to start FastAPI server
echo Starting FastAPI Backend Server...
echo Command: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
echo.

cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level info

if %errorlevel% neq 0 (
    echo.
    echo Error: Failed to start backend server
    echo Make sure FastAPI and Uvicorn are installed:
    echo   pip install fastapi uvicorn
    pause
    exit /b 1
)
