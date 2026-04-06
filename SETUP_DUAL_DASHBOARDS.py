#!/usr/bin/env python3
"""
OSIN Dual Dashboard Setup Assistant
Provides complete instructions for implementing both terminal and React 3D dashboards
"""

setup_guide = """
╔════════════════════════════════════════════════════════════════════════════╗
║                  OSIN DUAL DASHBOARD SETUP GUIDE                          ║
║        Terminal Dashboard + React 3D Intelligence Dashboard                ║
╚════════════════════════════════════════════════════════════════════════════╝

PROJECT STRUCTURE
─────────────────────────────────────────────────────────────────────────────
OSIN/
├── frontend/                          # Terminal Dashboard (EXISTING) ✅
│   ├── index.html
│   ├── app.js
│   └── style.css
│
├── dashboard/                         # React 3D Dashboard (NEW) 📦
│   ├── package.json
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── App.css
│   │   ├── components/
│   │   │   ├── Globe.tsx
│   │   │   ├── ThreatBar.tsx
│   │   │   ├── SourcePanel.tsx
│   │   │   ├── LiveFeed.tsx
│   │   │   └── Alerts.tsx
│   │   ├── hooks/
│   │   │   └── useWebSocket.ts
│   │   ├── store/
│   │   │   └── useStore.ts
│   │   ├── types/
│   │   │   └── index.ts
│   │   └── styles/
│   │       ├── live-feed.css
│   │       ├── alerts.css
│   │       ├── threat-bar.css
│   │       └── source-panel.css
│   └── public/
│
└── backend/                           # Backend API (ENHANCED) ⚙️
    ├── app/
    │   ├── main.py                    # ✅ Updated with WebSocket
    │   ├── api/
    │   └── ...
    └── requirements.txt


STEP-BY-STEP SETUP
─────────────────────────────────────────────────────────────────────────────

PHASE 1: PREPARE ENVIRONMENT
─────────────────────────────────────────────────────────────────────────────

Step 1.1: Verify Python and Node.js installed
```bash
python --version          # Should be 3.9+
node --version           # Should be 16+
npm --version
```

If Node.js not installed:
  → Download from https://nodejs.org/ (LTS version)
  → Run installer

Step 1.2: Create dashboard directory structure
```bash
cd C:\Users\User\Documents\OSIN
create_dashboard_dirs.bat
```

This creates:
  ✓ dashboard/src/components
  ✓ dashboard/src/hooks
  ✓ dashboard/src/store
  ✓ dashboard/src/types
  ✓ dashboard/src/styles
  ✓ dashboard/public


PHASE 2: SETUP BACKEND
─────────────────────────────────────────────────────────────────────────────

Step 2.1: Backend is already enhanced with WebSocket
         (Check: backend/app/main.py has WebSocket support)

Step 2.2: Start backend (Terminal 1)
```bash
cd C:\Users\User\Documents\OSIN\backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
  ✓ "Uvicorn running on http://0.0.0.0:8000"
  ✓ WebSocket available at ws://localhost:8000/ws/intelligence

Step 2.3: Verify backend is running
```bash
# In another terminal or browser
curl http://localhost:8000/health
```

Should return: {"status": "healthy"}


PHASE 3: SETUP REACT DASHBOARD
─────────────────────────────────────────────────────────────────────────────

Step 3.1: Initialize npm project (Terminal 2)
```bash
cd C:\Users\User\Documents\OSIN\dashboard
npm init -y
```

Step 3.2: Install dependencies
```bash
npm install react react-dom react-router-dom zustand
npm install three react-globe.gl
npm install --save-dev typescript vite @vitejs/plugin-react
npm install --save-dev @types/react @types/react-dom
npm install --save-dev tailwindcss postcss autoprefixer
```

Step 3.3: Create configuration files
  Copy the following from DASHBOARD_SOURCE_CODE.md:
  
  → dashboard/vite.config.ts
  → dashboard/tsconfig.json
  → dashboard/index.html

Step 3.4: Create source files
  Copy these to dashboard/src/ from DASHBOARD_SOURCE_CODE.md:
  
  → types/index.ts
  → store/useStore.ts
  → hooks/useWebSocket.ts
  → components/Globe.tsx
  → components/ThreatBar.tsx
  → components/SourcePanel.tsx
  → components/LiveFeed.tsx
  → components/Alerts.tsx
  → App.tsx
  → App.css
  → main.tsx

Step 3.5: Create CSS files
  Copy these to dashboard/src/styles/ from DASHBOARD_STYLES.md:
  
  → live-feed.css
  → alerts.css
  → threat-bar.css
  → source-panel.css

Step 3.6: Start dev server
```bash
npm run dev
```

Expected output:
  ✓ "VITE v4.x.x  ready in XXX ms"
  ✓ "Local: http://localhost:5173"


PHASE 4: ACCESSING DASHBOARDS
─────────────────────────────────────────────────────────────────────────────

With all three services running:

✅ React 3D Dashboard
   → http://localhost:5173
   → Full 3D globe, real-time alerts, live feed
   
✅ Terminal Dashboard
   → file:///C:/Users/User/Documents/OSIN/frontend/index.html
   → Terminal-style UI, live intelligence signals
   
✅ Backend API
   → http://localhost:8000
   → REST endpoints, health check
   
✅ WebSocket Stream
   → ws://localhost:8000/ws/intelligence
   → Real-time event stream (automatic)
   
✅ API Documentation
   → http://localhost:8000/docs (Swagger UI)


DATA FLOW
─────────────────────────────────────────────────────────────────────────────

Intelligence Sources
        ↓
Backend Intelligence Pipeline
        ↓
WebSocket Stream
        ├→ React Dashboard (3D visualization)
        └→ Mock Data Generator (simulates live events)
        
Both dashboards receive real-time data:
  • Live signals with confidence scores
  • Threat level assessments
  • Source distribution statistics
  • Geographic location data


FEATURES SUMMARY
─────────────────────────────────────────────────────────────────────────────

React 3D Dashboard:
  ✅ Interactive 3D globe with event visualization
  ✅ Real-time threat assessment bar
  ✅ Live intelligence feed
  ✅ Alert system with priority levels
  ✅ Source statistics and distribution
  ✅ WebSocket real-time updates
  ✅ Responsive design
  ✅ Professional cyberpunk UI

Terminal Dashboard:
  ✅ Terminal-style interface
  ✅ Live intelligence feed
  ✅ Real-time threat assessment
  ✅ Trending keywords tracking
  ✅ Source distribution metrics
  ✅ System status monitoring
  ✅ Mock data simulation


TROUBLESHOOTING
─────────────────────────────────────────────────────────────────────────────

Issue: Port 5173 already in use
Solution: npm run dev -- --port 5174

Issue: WebSocket connection failed
Solution: 
  1. Check backend is running: curl http://localhost:8000/health
  2. Check CORS enabled in backend
  3. Restart dev server

Issue: Module not found errors
Solution: npm install

Issue: TypeScript errors
Solution: npm install --save-dev typescript

Issue: "Cannot find module 'react-globe.gl'"
Solution: npm install react-globe.gl

Issue: Backend not streaming data
Solution: 
  1. Check main.py has WebSocket endpoint
  2. Restart uvicorn
  3. Check console for errors


TERMINAL COMMANDS REFERENCE
─────────────────────────────────────────────────────────────────────────────

Backend:
```bash
cd C:\Users\User\Documents\OSIN\backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

React Dashboard:
```bash
cd C:\Users\User\Documents\OSIN\dashboard
npm run dev
```

Terminal Dashboard:
```
Open: file:///C:/Users/User/Documents/OSIN/frontend/index.html
```

Build for Production:
```bash
cd C:\Users\User\Documents\OSIN\dashboard
npm run build
npm run preview
```


NEXT STEPS
─────────────────────────────────────────────────────────────────────────────

1. ✅ Set up backend with WebSocket (DONE)
2. ☐ Create React project structure
3. ☐ Copy all component files
4. ☐ Copy all style files
5. ☐ Start backend server
6. ☐ Start React dev server
7. ☐ Open dashboards in browser
8. ☐ Verify real-time data streaming
9. ☐ Build for production
10. ☐ Deploy to GitHub


REFERENCE FILES
─────────────────────────────────────────────────────────────────────────────

All source code provided in:
  → DASHBOARD_SOURCE_CODE.md (Component code)
  → DASHBOARD_STYLES.md (CSS styles)
  → DASHBOARD_IMPLEMENTATION.md (Detailed setup)

These files contain complete, copy-paste-ready code.


ADDITIONAL RESOURCES
─────────────────────────────────────────────────────────────────────────────

React: https://react.dev
TypeScript: https://www.typescriptlang.org
Vite: https://vitejs.dev
Three.js: https://threejs.org
Zustand: https://github.com/pmndrs/zustand
FastAPI WebSocket: https://fastapi.tiangolo.com/advanced/websockets/


SUCCESS CRITERIA
─────────────────────────────────────────────────────────────────────────────

✅ Backend running and serving API
✅ WebSocket streaming intelligence events
✅ React dashboard renders at localhost:5173
✅ Terminal dashboard displays live signals
✅ Real-time data visible in both dashboards
✅ Threat levels updating in real-time
✅ Alerts displaying with priorities
✅ 3D globe rendering with event points
✅ Navigation between dashboards working
✅ No console errors


ESTIMATED TIME
─────────────────────────────────────────────────────────────────────────────

Environment Setup:     10 minutes
Backend Enhancement:    5 minutes (already done)
React Setup:           15 minutes
Component Creation:    20 minutes
Testing & Debug:       15 minutes
────────────────────────────────
Total:                ~65 minutes


SUPPORT & DEBUGGING
─────────────────────────────────────────────────────────────────────────────

Terminal Dashboard:
  - Open browser console (F12) for errors
  - Check frontend/app.js for logic
  - Mock data generated every 3-5 seconds

React Dashboard:
  - Check console for WebSocket errors
  - Verify backend endpoint: http://localhost:8000/health
  - Check network tab for WebSocket connection

Backend:
  - Check uvicorn terminal for error messages
  - Verify port 8000 is not blocked
  - Check app/main.py for WebSocket implementation

────────────────────────────────────────────────────────────────────────────

Questions? Check DASHBOARD_IMPLEMENTATION.md for detailed setup instructions.
All code available in DASHBOARD_SOURCE_CODE.md and DASHBOARD_STYLES.md.

═════════════════════════════════════════════════════════════════════════════
                           READY TO BUILD! 🚀
═════════════════════════════════════════════════════════════════════════════
"""

print(setup_guide)

# Quick summary
print("\n" + "="*80)
print("QUICK SUMMARY")
print("="*80)
print("""
1. Backend: Already enhanced with WebSocket ✅
2. Terminal Dashboard: Already created ✅
3. React Dashboard: Ready to create
   - Has package.json, vite.config, tsconfig
   - Has all component code in DASHBOARD_SOURCE_CODE.md
   - Has all styles in DASHBOARD_STYLES.md

Next steps:
  1. cd dashboard && npm install
  2. Copy component files from DASHBOARD_SOURCE_CODE.md
  3. Copy styles from DASHBOARD_STYLES.md
  4. npm run dev
  5. Start backend: python -m uvicorn app.main:app --reload

Access:
  • React: http://localhost:5173
  • Terminal: file:///C:/Users/User/Documents/OSIN/frontend/index.html
  • Backend: http://localhost:8000
""")
