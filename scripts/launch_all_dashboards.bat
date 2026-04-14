@echo off
REM OSIN Complete Dashboard Launcher
REM Starts both backend and frontend with one command

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║   OSIN INTELLIGENCE DASHBOARD - COMPLETE LAUNCHER             ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

cd /d C:\Users\User\Documents\OSIN

echo [1/4] Checking directories...
if not exist "frontend" (
    echo ✗ Frontend directory not found!
    pause
    exit /b 1
)
if not exist "backend" (
    echo ✗ Backend directory not found!
    pause
    exit /b 1
)
if not exist "dashboard" (
    echo ⚠ React dashboard not found (optional)
)
echo ✓ Directories verified

echo.
echo [2/4] Starting Backend Server...
echo.

REM Start backend in new window
start cmd /k "cd /d C:\Users\User\Documents\OSIN\backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM Wait for backend to start
echo ⏳ Waiting for backend to initialize... (5 seconds)
timeout /t 5 /nobreak

echo ✓ Backend started on http://localhost:8000

echo.
echo [3/4] Opening Dashboards...
echo.

REM Open Terminal Dashboard
echo Launching Terminal Dashboard...
start "" "file:///C:/Users/User/Documents/OSIN/frontend/index.html"
timeout /t 2 /nobreak

REM Open API Docs
echo Launching API Documentation...
start "" "http://localhost:8000/docs"
timeout /t 2 /nobreak

REM Check if React dashboard exists
if exist "C:\Users\User\Documents\OSIN\dashboard\package.json" (
    echo.
    echo Would you like to start React 3D Dashboard? (Y/N)
    set /p reactstart=
    if /i "!reactstart!"=="Y" (
        echo Starting React dashboard...
        start cmd /k "cd /d C:\Users\User\Documents\OSIN\dashboard && npm run dev"
        timeout /t 10 /nobreak
        echo Launching React dashboard...
        start "" "http://localhost:5173"
    )
)

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                    ✓ DASHBOARDS LAUNCHED                      ║
echo ╠════════════════════════════════════════════════════════════════╣
echo ║                                                                ║
echo ║  AVAILABLE:                                                    ║
echo ║  • Terminal Dashboard (File):                                  ║
echo ║    file:///C:/Users/User/Documents/OSIN/frontend/index.html   ║
echo ║                                                                ║
echo ║  • API Documentation:                                          ║
echo ║    http://localhost:8000/docs                                  ║
echo ║                                                                ║
echo ║  • Health Check:                                               ║
echo ║    http://localhost:8000/health                                ║
echo ║                                                                ║
if exist "C:\Users\User\Documents\OSIN\dashboard\src\App.tsx" (
    echo ║  • React 3D Dashboard:                                       ║
    echo ║    http://localhost:5173                                     ║
    echo ║                                                                ║
)
echo ║  Backend running on: http://0.0.0.0:8000                      ║
echo ║  WebSocket: ws://localhost:8000/ws/intelligence                ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo Press any key to continue monitoring...
pause
