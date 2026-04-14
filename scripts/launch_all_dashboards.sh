#!/bin/bash
# OSIN Complete Dashboard Launcher (macOS/Linux)

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   OSIN INTELLIGENCE DASHBOARD - COMPLETE LAUNCHER             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

cd ~/Documents/OSIN 2>/dev/null || cd /Users/User/Documents/OSIN 2>/dev/null || cd C:/Users/User/Documents/OSIN

echo "[1/4] Checking directories..."
if [ ! -d "frontend" ]; then
    echo "✗ Frontend directory not found!"
    exit 1
fi
if [ ! -d "backend" ]; then
    echo "✗ Backend directory not found!"
    exit 1
fi
echo "✓ Directories verified"

echo ""
echo "[2/4] Starting Backend Server..."
echo ""

# Start backend
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "⏳ Waiting for backend to initialize... (5 seconds)"
sleep 5

echo "✓ Backend started on http://localhost:8000"

cd ..

echo ""
echo "[3/4] Opening Dashboards..."
echo ""

# Open Terminal Dashboard
echo "Launching Terminal Dashboard..."
open "file://$(pwd)/frontend/index.html" 2>/dev/null || xdg-open "file://$(pwd)/frontend/index.html"
sleep 2

# Open API Docs
echo "Launching API Documentation..."
open "http://localhost:8000/docs" 2>/dev/null || xdg-open "http://localhost:8000/docs"
sleep 2

# Check for React dashboard
if [ -f "dashboard/package.json" ]; then
    read -p "Start React 3D Dashboard? (Y/N): " reactstart
    if [[ "$reactstart" =~ ^[Yy]$ ]]; then
        echo "Starting React dashboard..."
        cd dashboard
        npm run dev &
        REACT_PID=$!
        sleep 10
        echo "Launching React dashboard..."
        open "http://localhost:5173" 2>/dev/null || xdg-open "http://localhost:5173"
        cd ..
    fi
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    ✓ DASHBOARDS LAUNCHED                      ║"
echo "╠════════════════════════════════════════════════════════════════╣"
echo "║                                                                ║"
echo "║  AVAILABLE:                                                    ║"
echo "║  • Terminal Dashboard:                                         ║"
echo "║    file://$(pwd)/frontend/index.html                           ║"
echo "║                                                                ║"
echo "║  • API Documentation:                                          ║"
echo "║    http://localhost:8000/docs                                  ║"
echo "║                                                                ║"
echo "║  • Health Check:                                               ║"
echo "║    http://localhost:8000/health                                ║"
echo "║                                                                ║"
[ -f "dashboard/src/App.tsx" ] && echo "║  • React 3D Dashboard: http://localhost:5173                  ║"
echo "║                                                                ║"
echo "║  Backend: http://0.0.0.0:8000                                  ║"
echo "║  WebSocket: ws://localhost:8000/ws/intelligence                ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Dashboards running. Press Ctrl+C to stop."
echo ""

# Wait for processes
wait $BACKEND_PID 2>/dev/null
