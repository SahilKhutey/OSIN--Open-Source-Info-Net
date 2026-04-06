@echo off
REM Advanced OSIN 3D Intelligence Dashboard Launcher
REM Features: Three.js 3D Globe with Clustering, Heatmaps, and Real-time Event Analysis

setlocal enabledelayedexpansion

echo.
echo =====================================================
echo   OSIN ADVANCED INTELLIGENCE DASHBOARD v2.0
echo =====================================================
echo.
echo This launcher will:
echo 1. Install npm dependencies (if needed)
echo 2. Start the React development server
echo 3. Open the dashboard in your default browser
echo.
echo Features:
echo   - 3D Interactive Globe with Three.js
echo   - Automatic event clustering (DBSCAN algorithm)
echo   - Real-time heatmap generation
echo   - Animated cluster visualization
echo   - Live event feed with severity coloring
echo   - Source statistics panel
echo   - Activity hotspot detection
echo.
echo =====================================================
echo.

cd /d C:\Users\User\Documents\OSIN\dashboard

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing dependencies (first run only)...
    call npm install
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
    echo Dependencies installed successfully!
)

echo.
echo Starting React development server on http://localhost:5173
echo.
echo Press Ctrl+C to stop the server
echo.

start http://localhost:5173

npm run dev
