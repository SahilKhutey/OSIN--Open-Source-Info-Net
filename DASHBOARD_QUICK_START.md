# 🎯 OSIN Dashboard Quick Start Guide

## ✅ What's Ready

You now have **THREE complete dashboards**:

### 1. **Terminal Dashboard** (HTML/JS)
   - File-based, no build needed
   - Live feed, threats, source metrics
   - Simple and lightweight
   - Location: `C:\Users\User\Documents\OSIN\frontend\`

### 2. **React 3D Dashboard** (NEW!)
   - Interactive 3D globe with events
   - Heatmap visualization
   - Real-time source tracking
   - Professional UI
   - Location: `C:\Users\User\Documents\OSIN\dashboard\`

### 3. **API Documentation**
   - Interactive API docs
   - Try endpoints
   - Schema reference
   - Location: `http://localhost:8000/docs`

---

## 🚀 Launch Everything in One Command

### Option 1: Windows Batch (EASIEST)
```cmd
cd C:\Users\User\Documents\OSIN
launch_all_dashboards.bat
```
✅ Automatically starts backend, opens all dashboards

### Option 2: Python Cross-Platform
```bash
cd C:\Users\User\Documents\OSIN
python launch_all_dashboards.py
```

### Option 3: Manual Launch

**Terminal 1 - Backend:**
```bash
cd C:\Users\User\Documents\OSIN\backend
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - React Dashboard:**
```bash
cd C:\Users\User\Documents\OSIN\dashboard
npm install  # Only first time
npm run dev
```

**Then open in browser:**
- 🟢 Terminal: http://localhost:8000/index.html
- 🟢 React 3D: http://localhost:5173
- 🟢 API Docs: http://localhost:8000/docs

---

## 📊 Dashboard Components

### React 3D Dashboard Features

| Component | Purpose | Location |
|-----------|---------|----------|
| **3D Globe** | Visualize events globally | Center screen, full height |
| **Heatmap** | Show signal density | Toggle with 3D mode |
| **Live Feed** | Real-time events | Top right |
| **Alerts** | Active alerts | Top right (below feed) |
| **Sources** | Twitter, Reddit, YouTube, News | Bottom right |
| **Threat** | Threat level indicator | Bottom right |

### Color Scheme
- 🟢 **Green (#00ff00)** - Normal, low threat
- 🟡 **Yellow (#ffff00)** - Medium
- 🟠 **Orange (#ff6600)** - High
- 🔴 **Red (#ff0000)** - Critical

---

## 🔌 WebSocket Data Format

Send data to `ws://localhost:8000/ws/intelligence`:

### Add Event
```json
{
  "type": "event",
  "payload": {
    "id": "evt-001",
    "timestamp": "2024-01-20T10:30:00Z",
    "source": "twitter",
    "content": "Intelligence signal about security threat",
    "severity": "high",
    "location": {
      "lat": 40.7128,
      "lng": -74.0060,
      "country": "USA"
    },
    "tags": ["security", "trending"]
  }
}
```

### Add Alert
```json
{
  "type": "alert",
  "payload": {
    "id": "alert-001",
    "timestamp": "2024-01-20T10:30:00Z",
    "severity": "critical",
    "title": "Critical Alert",
    "description": "Potential security breach detected",
    "type": "anomaly"
  }
}
```

### Update Source Stats
```json
{
  "type": "stats",
  "payload": {
    "twitter": 250,
    "reddit": 180,
    "youtube": 95,
    "news": 420,
    "instagram": 150,
    "linkedin": 80,
    "total": 1175
  }
}
```

### Update Threat Level
```json
{
  "type": "threat",
  "payload": {
    "level": 72.5
  }
}
```

---

## 📁 File Structure

```
C:\Users\User\Documents\OSIN\
├── dashboard/                          ← React 3D Dashboard
│   ├── src/
│   │   ├── components/                 ← UI Components
│   │   │   ├── Dashboard.tsx           ← Main layout
│   │   │   ├── EnhancedGlobe.tsx       ← 3D globe
│   │   │   ├── HeatmapGlobe.tsx        ← Heatmap
│   │   │   ├── SourcePanel.tsx         ← Sources info
│   │   │   ├── LiveFeed.tsx            ← Events feed
│   │   │   ├── Alerts.tsx              ← Alerts
│   │   │   └── ThreatBar.tsx           ← Threat level
│   │   ├── store/useStore.ts           ← State management
│   │   ├── services/websocketService.ts ← WebSocket
│   │   └── styles/                     ← CSS files
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                            ← FastAPI Backend
│   ├── app/
│   │   ├── main.py                    ← Entry point
│   │   └── ...
│   └── requirements.txt
│
├── frontend/                           ← Terminal Dashboard
│   ├── index.html
│   ├── app.js
│   └── style.css
│
└── launch_all_dashboards.bat          ← Master launcher
```

---

## 💻 System Requirements

- **Node.js 16+** (for React dashboard)
- **Python 3.8+** (for backend)
- **npm or yarn** (JavaScript package manager)
- **Modern browser** (Chrome, Firefox, Safari, Edge)

---

## 🔧 Setup Instructions

### First Time Setup

1. **Install Node.js**
   - Download from: https://nodejs.org
   - Choose LTS version
   - Install globally

2. **Install dashboard dependencies**
   ```bash
   cd C:\Users\User\Documents\OSIN\dashboard
   npm install
   ```
   ⏱️ Takes 2-3 minutes

3. **Install backend dependencies** (if not already done)
   ```bash
   cd C:\Users\User\Documents\OSIN\backend
   pip install -r requirements.txt
   ```

4. **Run everything**
   ```bash
   .\launch_all_dashboards.bat
   ```

---

## 🎮 Usage

### View Real-Time Intelligence

1. **Open React Dashboard**
   - Navigate to http://localhost:5173
   - See 3D globe with events

2. **Switch to Heatmap**
   - Click "HEATMAP" button
   - See signal density by region

3. **Monitor Sources**
   - Check right panel for source breakdown
   - See real-time counts updating

4. **Watch Threat Level**
   - See color-coded threat indicator
   - Ranges from GREEN to RED

5. **Acknowledge Alerts**
   - Click "ACK" button on each alert
   - Dismisses from active list

### Send Test Data

Use backend endpoints or WebSocket to send events:

```bash
# REST API example
curl -X POST http://localhost:8000/api/events \
  -H "Content-Type: application/json" \
  -d '{
    "source": "twitter",
    "content": "Test event",
    "severity": "high",
    "location": {"lat": 40.7128, "lng": -74.0060}
  }'
```

Or connect WebSocket client and send JSON messages.

---

## 🐛 Troubleshooting

### Dashboard won't load?
- ✅ Check http://localhost:5173 in browser
- ✅ Ensure `npm run dev` is running
- ✅ Check for port conflicts (lsof -i :5173)
- ✅ Clear browser cache (Ctrl+Shift+Del)

### No data appearing?
- ✅ Check backend running on port 8000
- ✅ Send test data to WebSocket
- ✅ Check browser console for errors
- ✅ Verify WebSocket connection in DevTools

### Globe not rendering?
- ✅ Check browser WebGL support
- ✅ Try heatmap mode instead
- ✅ Update graphics drivers
- ✅ Try different browser

### Backend connection fails?
- ✅ Ensure backend running: `python -m uvicorn app.main:app --reload`
- ✅ Check port 8000 available
- ✅ Check firewall settings
- ✅ Verify IP/hostname

---

## 📈 Performance Tips

1. **Limit event history** - Dashboard keeps last 100 events
2. **Use heatmap for many points** - 3D globe slower with 500+ points
3. **Reduce refresh rate** - Backend batches updates
4. **Close unused dashboards** - Save CPU/memory
5. **Update graphics drivers** - Better 3D performance

---

## 🎨 Customization

### Change Colors
Edit `src/styles/*.css` files:
```css
/* Current colors */
--primary: #00ff00;    /* Bright green */
--critical: #ff0000;   /* Red */
--high: #ff6600;       /* Orange */
--medium: #ffff00;     /* Yellow */
--low: #00ff00;        /* Green */
--background: #000;    /* Black */
```

### Change Globe Imagery
In `EnhancedGlobe.tsx`:
```typescript
globeImageUrl="//your-image-url"
bumpImageUrl="//your-bump-map-url"
```

### Adjust Layout
Edit `src/styles/Dashboard.css` grid:
```css
.dashboard-grid {
  grid-template-columns: 1fr 300px;  /* Adjust sidebar width */
  gap: 15px;  /* Increase spacing */
}
```

---

## 📚 Documentation

- **React Dashboard README**: `C:\Users\User\Documents\OSIN\dashboard\README.md`
- **Full Implementation**: `C:\Users\User\Documents\OSIN\REACT_DASHBOARD_IMPLEMENTATION.md`
- **API Docs**: http://localhost:8000/docs (when running)

---

## 🎯 Next Steps

1. ✅ Run `launch_all_dashboards.bat`
2. ✅ Open http://localhost:5173
3. ✅ Send test data via WebSocket
4. ✅ Monitor real-time intelligence
5. ✅ Customize styling as needed

---

## 📞 Quick Commands Reference

```bash
# Start everything
launch_all_dashboards.bat

# Start just React dashboard
cd dashboard && npm run dev

# Start just backend
cd backend && python -m uvicorn app.main:app --reload

# Build for production
cd dashboard && npm run build

# Install dependencies
cd dashboard && npm install
```

---

## ✨ Features Summary

✅ **3D Interactive Globe** - Visualize global intelligence  
✅ **Heatmap Mode** - See signal density by region  
✅ **Live Feed** - Real-time event stream  
✅ **6+ Sources** - Track Twitter, Reddit, YouTube, News, Instagram, LinkedIn  
✅ **Alert System** - Manage critical alerts  
✅ **Threat Level** - Color-coded threat indicator  
✅ **WebSocket** - Real-time data streaming  
✅ **Responsive** - Works on desktop, tablet, mobile  
✅ **Type-Safe** - Full TypeScript  
✅ **Production-Ready** - Vite build system  

---

🎉 **Your OSIN Dashboard is ready to go!**

Start with: `.\launch_all_dashboards.bat`
