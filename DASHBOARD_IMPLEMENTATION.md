# OSIN 3D Dashboard - Complete Implementation Guide

This guide will help you set up the advanced React 3D dashboard alongside the existing terminal dashboard.

## Quick Setup (5 minutes)

### 1. Create Dashboard Directory Structure
```bash
cd c:\Users\User\Documents\OSIN
create_dashboard_dirs.bat
```

### 2. Install Node.js & npm (if not installed)
Download from: https://nodejs.org/ (LTS version)

### 3. Navigate to Dashboard & Install Dependencies
```bash
cd dashboard
npm install
```

### 4. Start Development Server
```bash
npm run dev
```

Dashboard will be available at: `http://localhost:5173`

## File Structure to Create

After running the setup, create these files:

### TypeScript Types: `src/types/index.ts`
[See dashboard-types.ts file]

### Store (Zustand): `src/store/useStore.ts`
[See dashboard-store.ts file]

### WebSocket Hook: `src/hooks/useWebSocket.ts`
[See dashboard-websocket.ts file]

### Globe Component: `src/components/Globe.tsx`
[See components/Globe.tsx file]

### Threat Bar: `src/components/ThreatBar.tsx`
[See components/ThreatBar.tsx file]

### Source Panel: `src/components/SourcePanel.tsx`
[See components/SourcePanel.tsx file]

### Live Feed: `src/components/LiveFeed.tsx`
[See components/LiveFeed.tsx file]

### Alerts: `src/components/Alerts.tsx`
[See components/Alerts.tsx file]

### Main App: `src/App.tsx`
[See App.tsx file]

### Styles: `src/App.css`
[See App.css file]

### Main Entry: `src/main.tsx`
```typescript
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './App.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

### HTML Entry: `index.html`
```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>OSIN 3D Dashboard</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

### TypeScript Config: `tsconfig.json`
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,

    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",

    /* Linting */
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### Vite Config: `vite.config.ts`
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true
      }
    }
  }
})
```

## Backend Changes

The backend has been updated with:

1. **WebSocket Support** - `/ws/intelligence` endpoint
2. **CORS Enabled** - Allows frontend requests
3. **Mock Data Generator** - Generates continuous event stream
4. **Connection Manager** - Handles multiple client connections

### Start Backend
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Architecture Overview

### Data Flow
```
Intelligence Sources (Twitter, Reddit, etc.)
        ↓
Backend Intelligence Pipeline
        ↓
WebSocket Stream (/ws/intelligence)
        ↓
React Dashboard (Client)
        ↓
Components (Globe, Alerts, Feed)
```

### Components Hierarchy
```
App
├── Nav
├── Dashboard
│   ├── LiveFeed
│   ├── Alerts
│   ├── Globe
│   ├── SourcePanel
│   └── ThreatBar
└── Terminal (Route)
```

### State Management
```
useStore (Zustand)
├── events: IntelligenceEvent[]
├── alerts: Alert[]
├── sourceStats: SourceStats
├── threatLevel: number
└── Actions (add, update, etc.)
```

## Running Both Dashboards

### Terminal 1: Backend
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2: React Dashboard
```bash
cd dashboard
npm run dev
```

### Terminal 3: Terminal Dashboard (Optional)
Open in browser: `file:///C:/Users/User/Documents/OSIN/frontend/index.html`

## Access URLs

- **React Dashboard**: http://localhost:5173
- **Terminal Dashboard**: file:///C:/Users/User/Documents/OSIN/frontend/index.html
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/ws/intelligence

## Troubleshooting

### "Port 5173 already in use"
```bash
npm run dev -- --port 5174
```

### "WebSocket connection failed"
- Check backend is running: `http://localhost:8000/health`
- Check CORS headers in backend

### "Module not found"
```bash
npm install
npm run dev
```

### "TypeScript errors"
```bash
npm install --save-dev typescript @types/react @types/react-dom
```

## Build for Production

```bash
npm run build
npm run preview
```

This creates a production-ready bundle in `dist/` folder.

## Next Steps

1. ✅ Create directory structure
2. ✅ Install dependencies
3. ✅ Create component files
4. ✅ Start backend with WebSocket
5. ✅ Launch React dev server
6. ✅ Connect to live data stream
7. ✅ Deploy as needed

## Features Summary

✅ 3D Globe Visualization  
✅ Real-time Event Streaming  
✅ Threat Assessment  
✅ Alert Management  
✅ Source Statistics  
✅ Terminal Interface  
✅ TypeScript Type Safety  
✅ Responsive Design  
✅ WebSocket Integration  

---

For detailed file contents, see the individual component files below.
