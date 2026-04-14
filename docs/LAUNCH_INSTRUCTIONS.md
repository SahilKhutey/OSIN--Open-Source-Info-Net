# 🚀 OSIN Dashboard - LAUNCH INSTRUCTIONS

## ⚡ QUICK START (Copy & Paste)

### Windows PowerShell
```powershell
cd C:\Users\User\Documents\OSIN
python launch_dashboards.py
```

### Windows Command Prompt
```cmd
cd C:\Users\User\Documents\OSIN
launch_dashboards.bat
```

---

## ✅ What Happens When You Launch

1. **Backend Checks**
   - ✓ Python version verified (3.9+)
   - ✓ FastAPI detected
   - ✓ Uvicorn installed
   - ✓ Project structure validated

2. **Backend Starts**
   - ✓ FastAPI server starts on port 8000
   - ✓ Auto-reload enabled (changes reload instantly)
   - ✓ Rate limiting active (protection enabled)
   - ✓ Health check endpoint ready

3. **Dashboard Opens**
   - ✓ Browser opens automatically
   - ✓ Dashboard UI loads
   - ✓ Mock intelligence signals appear
   - ✓ Trends and forecasts visible

---

## 📊 Dashboard Access URLs

Once running:

| Purpose | URL |
|---------|-----|
| **Main Dashboard** | file:///C:/Users/User/Documents/OSIN/frontend/index.html |
| **API Docs (Interactive)** | http://localhost:8000/docs |
| **API Redoc** | http://localhost:8000/redoc |
| **Health Check** | http://localhost:8000/health |
| **Root API** | http://localhost:8000/ |

---

## 🎯 Dashboard Features Ready to Use

### Real-Time Intelligence Feed
- Live signal updates every 3 seconds
- Signal credibility scores (0.0 - 1.0)
- Threat level classification
- Combat readiness scoring
- Source attribution

### Threat Monitoring
- Current threat level indicator
- System status display
- OPSEC protocol status
- Active hotspot count

### Intelligence Analysis
- **Click any signal** to see credibility breakdown
  - Credibility score
  - Occurrence frequency
  - Reach/impact assessment
  - Proof type quality
  - Coverage analysis
  - Source diversity metrics

### Trend Analysis
- Top trending keywords
- Cross-platform detection
- Impact scoring
- Predictive indicators

### Multi-Domain View
- **SAT-IMG**: Satellite imagery status
- **SIGINT**: Signals intelligence status
- **LINGUA**: Language analysis status

### Action Console
- Quick tactical operations
- GHOST mode activation
- PHANTOM protocol engagement

---

## 🔧 How It Works

### Architecture
```
Browser                          Server
 │                               │
 ├─ frontend/index.html          │
 ├─ frontend/style.css           │
 ├─ frontend/app.js              │
 │                               │
 └─ HTTP Requests ────────────────┤
                                  │
                                  ├─ backend/app/main.py (FastAPI)
                                  ├─ app/api/router.py (Endpoints)
                                  ├─ app/config.py (Settings)
                                  │
                                  └─ Port 8000
```

### Request Flow
1. **Browser loads** `index.html`
2. **JavaScript loads** from `app.js`
3. **Render dashboard** with mock data
4. **API calls** to `http://localhost:8000/api/v1/signals`
5. **Live updates** every 3 seconds

---

## 📋 System Requirements

### Minimum Requirements
- ✅ Python 3.9 or higher
- ✅ 512 MB RAM
- ✅ 50 MB disk space
- ✅ Windows 10+ / macOS / Linux

### Required Packages (Auto-Installed)
```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
```

### Installation Check
```powershell
python --version              # Should show 3.9+
python -m pip list | grep fastapi  # Should show fastapi
```

---

## 🎨 Dashboard Visual Guide

```
┌─────────────────────────────────────────────────────────┐
│                    OSIN Intelligence Engine              │
│                 System Online: Global Extraction Active  │
└─────────────────────────────────────────────────────────┘

┌──────────────────┬──────────────────┬──────────────────┐
│ Battlefield      │ Conflict Forecast│ Counter-Intel    │
│ Situation        │ 02 Active        │ Normal           │
│                  │                  │                  │
│ Current Status   │ Hotspots         │ Monitoring       │
│ GREEN            │ 02 Active        │ Status           │
│                  │                  │                  │
│ Protocol: STABLE │                  │                  │
└──────────────────┴──────────────────┴──────────────────┘

┌────────────────────────────────┬──────────────────────┐
│                                │                      │
│  Combat-Ready Intelligence Feed│ Intelligence         │
│                                │ Forecasting Panel    │
│  ▌ social  X / Twitter         │                      │
│    "Trade volume increase..."  │ #QuantumLeap: 9.4   │
│    Combat: 78%  Yellow  2m ago │ MarketPivot: 8.2    │
│                                │ OSIN_v1: 7.9        │
│  ▌ news    Reuters             │                      │
│    "Central banks indicate..."  │ Multi-Domain Fusion │
│    Combat: 92%  Green  5m ago  │ SAT-IMG: ACTIVE     │
│                                │ SIGINT: SCANNING    │
│                                │ LINGUA: ONLINE      │
│                                │                      │
│                                │ Action Console      │
│                                │ [GHOST] [PHANTOM]   │
│                                │                      │
└────────────────────────────────┴──────────────────────┘
```

---

## 🐛 Troubleshooting

### Issue: "Port 8000 already in use"
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace XXXX with PID)
taskkill /PID XXXX /F

# OR: Use different port
python -m uvicorn app.main:app --port 8001
```

### Issue: "ModuleNotFoundError: No module named 'fastapi'"
```powershell
# Install FastAPI and dependencies
pip install fastapi uvicorn

# Or install from requirements
pip install -r requirements.txt
```

### Issue: "Dashboard not loading"
1. Check terminal for errors
2. Open http://localhost:8000/health (should show `{"status": "healthy"}`)
3. Check browser console (F12)
4. Clear browser cache (Ctrl+Shift+Delete)

### Issue: "Signals not updating"
1. Check browser console for errors
2. Check API endpoint: http://localhost:8000/docs
3. Try manual test: `curl http://localhost:8000/health`

### Issue: "TypeError: cannot use == with str and int"
- Update Python to 3.10+ OR
- Use older FastAPI: `pip install fastapi==0.99.1`

---

## 🎮 Interactive Features

### View Signal Details
1. **Click any signal** in the feed
2. **Modal pops up** showing credibility breakdown
3. **Review metrics**:
   - Credibility (0.0-1.0)
   - Occurrence frequency
   - Reach/impact score
   - Proof type quality
   - Coverage percentage
   - Source diversity

### Start Live Simulation
- **Auto-runs** when dashboard loads
- **Updates every 3 seconds** with new signals
- **Threat level changes** dynamically
- **Trends shift** in real-time

---

## 🔌 API Testing

### Using FastAPI Docs (Interactive)
1. Go to: http://localhost:8000/docs
2. Click any endpoint
3. Click "Try it out"
4. See live responses

### Using PowerShell
```powershell
# Health check
Invoke-WebRequest http://localhost:8000/health

# Get signals
Invoke-WebRequest http://localhost:8000/api/v1/signals
```

### Using curl (if installed)
```bash
# Health check
curl http://localhost:8000/health

# Get signals
curl http://localhost:8000/api/v1/signals
```

---

## 📊 Performance Metrics

### Expected Performance
- Dashboard Load: < 2 seconds
- Signal Refresh: Every 3 seconds
- API Response: < 100ms
- CPU Usage: < 5%
- Memory: < 100MB

### Monitoring
- Check **Task Manager** for resource usage
- Monitor **terminal logs** for errors
- Review **browser console** (F12) for client issues

---

## 🛑 Stopping the Dashboard

### Method 1: Keyboard (Easiest)
```
Press Ctrl+C in the terminal
```

### Method 2: Task Manager
1. Open Task Manager (Ctrl+Shift+Esc)
2. Find "Python" process
3. Right-click → End Task

### Method 3: Command Line
```powershell
taskkill /F /IM python.exe
```

---

## 🔄 Restarting

### After Stopping
Simply run again:
```powershell
python launch_dashboards.py
```

### Auto-Reload During Development
Changes to these files auto-reload:
- `backend/app/main.py`
- `backend/app/api/router.py`
- `frontend/app.js` (requires manual browser refresh)

---

## 📚 Next Steps

1. **Launch Dashboard**: `python launch_dashboards.py`
2. **Explore UI**: Click signals, view breakdowns
3. **Test API**: Go to http://localhost:8000/docs
4. **Review Code**: Check `frontend/app.js` and `backend/app/main.py`
5. **Connect Real Data**: See `backend/app/api/router.py`

---

## 📖 Additional Resources

### Documentation Files
- `DASHBOARD_GUIDE.md` - Detailed dashboard documentation
- `RUN_TESTS_GUIDE.md` - How to run test suite
- `QUICK_START.md` - Quick reference guide
- `README.md` - Project overview

### Project Structure
```
C:\Users\User\Documents\OSIN\
├── frontend/               # Dashboard UI
│   ├── index.html          # Main page
│   ├── app.js              # Dashboard logic
│   └── style.css           # Styling
├── backend/                # FastAPI server
│   ├── app/
│   │   ├── main.py         # FastAPI app
│   │   └── api/router.py   # API endpoints
│   └── requirements.txt
├── launch_dashboards.py    # Python launcher ← USE THIS
├── launch_dashboards.bat   # Batch launcher ← OR THIS
└── DASHBOARD_GUIDE.md      # Full documentation
```

---

## ✨ Features Overview

### ✅ Currently Available
- Real-time intelligence signal feed
- Threat level monitoring
- Credibility scoring system
- Trend analysis and forecasting
- Multi-domain intelligence fusion
- Combat readiness scoring
- Live signal simulation
- Interactive credibility breakdowns
- Action console for operations

### 🔨 Coming Soon
- Real database integration
- User authentication
- Advanced analytics
- Geospatial mapping
- Alert system
- Mobile optimization

---

## 💡 Tips & Tricks

### For Best Experience
1. **Maximize browser window** for full dashboard view
2. **Use Chrome/Edge** for best performance
3. **Keep F12 closed** (DevTools slows rendering)
4. **Allow pop-ups** for external signals
5. **Check logs** if something seems wrong

### Pro Tips
- Click signal header for credibility breakdown
- Watch trend scores change in real-time
- Monitor threat level transitions
- Use action console for tactical ops
- Reference multi-domain view for full picture

---

## 🎯 Success Checklist

When you see this, you're ready:
- ✅ Terminal shows "Uvicorn running on 0.0.0.0:8000"
- ✅ Browser opens dashboard automatically
- ✅ Dashboard displays with signals and trends
- ✅ Signals update every 3 seconds
- ✅ Clicking signals shows credibility breakdown
- ✅ API docs available at http://localhost:8000/docs

---

## 📞 Quick Reference

```
LAUNCH:           python launch_dashboards.py
DASHBOARD:        http://localhost:8000
API DOCS:         http://localhost:8000/docs
HEALTH CHECK:     http://localhost:8000/health
STOP:             Ctrl+C in terminal
RESTART:          python launch_dashboards.py
```

---

**Ready? Let's go! 🚀**

```powershell
cd C:\Users\User\Documents\OSIN
python launch_dashboards.py
```

---

*Last Updated: 2025-04-05*  
*Dashboard Version: 1.0*  
*Status: ✅ Ready for Launch*
