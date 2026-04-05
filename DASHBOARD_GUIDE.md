# 🎯 OSIN Dashboard Guide

## Quick Start

### 🚀 Launch Dashboard (3 Ways)

#### **Option 1: Python Script (Recommended)**
```powershell
cd C:\Users\User\Documents\OSIN
python launch_dashboards.py
```
✅ Automatically opens dashboard in browser  
✅ Full error checking and diagnostics  
✅ Professional startup banner  

#### **Option 2: Windows Batch File**
```cmd
cd C:\Users\User\Documents\OSIN
launch_dashboards.bat
```
✅ Simple one-click launch  
✅ No Python arguments needed  

#### **Option 3: Manual Uvicorn**
```powershell
cd C:\Users\User\Documents\OSIN\backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
✅ Direct control  
✅ Custom port configuration  

---

## 📊 Dashboard Overview

### Main Dashboard URL
```
file:///C:/Users/User/Documents/OSIN/frontend/index.html
```

### API Endpoints
```
Frontend:   http://localhost:8000 (after backend starts)
API Docs:   http://localhost:8000/docs
API Redoc:  http://localhost:8000/redoc
Health:     http://localhost:8000/health
```

---

## 🎨 Dashboard Features

### 1️⃣ **Battlefield Situation**
- Current threat level indicator
- System status display
- OPSEC protocol status

### 2️⃣ **Conflict Forecast**
- Active hotspot count
- Early warning indicators
- Trend predictions

### 3️⃣ **Counter-Intel Dashboard**
- Counter-intelligence monitoring
- Threat classifications
- Risk assessments

### 4️⃣ **Combat-Ready Intelligence Feed**
Real-time signal stream with:
- Source attribution (Twitter, Reuters, etc.)
- Signal type classification (social, news, etc.)
- Credibility scoring (0.0 - 1.0)
- Threat level assessment
- Combat readiness score
- Live timestamp

### 5️⃣ **Intelligence Forecasting**
- Trending keywords with impact scores
- Multi-platform detection
- Predictive analysis

### 6️⃣ **Multi-Domain Fusion**
Unified view of:
- **SAT-IMG**: Satellite Imagery status
- **SIGINT**: Signals Intelligence status
- **LINGUA**: Language Analysis status

### 7️⃣ **Action Console**
Quick-access operations:
- **GHOST Mode**: Stealth extraction
- **PHANTOM Protocol**: Advanced analysis

---

## 📡 Backend API Reference

### Get Intelligence Signals
```bash
GET /api/v1/signals
```

**Response:**
```json
{
  "signals": [
    {
      "id": 1,
      "type": "social",
      "source": "X / Twitter",
      "content": "Signal content...",
      "credibility": 0.85,
      "threat_level": "YELLOW",
      "combat_score": 0.78
    }
  ]
}
```

### Health Check
```bash
GET /health
```

**Response:**
```json
{
  "status": "healthy"
}
```

### Report Threat
```bash
POST /api/v1/threats
Content-Type: application/json

{
  "content": "Threat description",
  "source": "Detection source",
  "severity": "high"
}
```

---

## 🔧 Configuration

### Backend Configuration
**File**: `backend/app/config.py`

```python
class Settings:
    PROJECT_NAME = "OSIN Intelligence Engine"
    API_V1_STR = "/api/v1"
    
    # Rate limiting
    RATE_LIMIT_DURATION = 1.0  # seconds per request
    
    # Server
    HOST = "0.0.0.0"
    PORT = 8000
```

### Frontend Configuration
**File**: `frontend/app.js`

```javascript
// Mock data configuration
const mockSignals = [/* ... */];
const mockTrends = [/* ... */];

// Update interval (seconds)
const LIVE_UPDATE_INTERVAL = 3;
```

---

## 🛠️ Development & Debugging

### Browser Developer Tools
1. Press `F12` to open Developer Tools
2. **Console Tab**: Check for JavaScript errors
3. **Network Tab**: Monitor API calls
4. **Elements Tab**: Inspect HTML/CSS

### Backend Logs
Terminal output shows:
- Request/response logs
- API call details
- Error traces
- Performance metrics

### Common Issues & Solutions

#### ❌ **Port 8000 Already in Use**
```powershell
# Find and kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# OR use different port
python -m uvicorn app.main:app --port 8001
```

#### ❌ **Dashboard Won't Open**
1. Check if backend started (look for "Uvicorn running on")
2. Manually open: `http://localhost:8000`
3. Check browser console for errors (F12)

#### ❌ **API Not Responding**
1. Verify backend is running in terminal
2. Check: `http://localhost:8000/health`
3. If still failing, restart with: `Ctrl+C` then relaunch

#### ❌ **Module Not Found Error**
```powershell
# Install missing dependencies
pip install -r requirements.txt
```

---

## 📊 Sample Data

Dashboard loads with **mock data** by default:

### Sample Signals
```javascript
{
  id: 1,
  type: 'social',
  source: 'X / Twitter',
  content: 'Significant increase in trade volume detected...',
  credibility: 0.85,
  threat_level: 'YELLOW',
  combat_score: 0.78
}
```

### Sample Trends
```javascript
{
  keyword: '#QuantumLeap',
  score: 9.4,
  platforms: ['X', 'Reddit']
}
```

---

## 🎯 Use Cases

### 1. **Real-Time Monitoring**
- Watch live signal feed
- Monitor threat levels
- Track trending topics

### 2. **Intelligence Analysis**
- Click signals for credibility breakdown
- Review source attribution
- Assess combat readiness

### 3. **Trend Forecasting**
- Identify emerging patterns
- Track keyword velocity
- Predict escalation

### 4. **Operations Planning**
- Use action console for tactical operations
- Reference multi-domain fusion view
- Coordinate inter-agency intelligence

---

## 📈 Performance Metrics

### Expected Performance
- **Dashboard Load Time**: < 2 seconds
- **Signal Refresh Rate**: 3 seconds
- **API Response Time**: < 100ms
- **CPU Usage**: < 5%
- **Memory Usage**: < 100MB

### Optimization Tips
1. **Browser Cache**: Clear cache if UI doesn't update
2. **Console Logs**: Disable in production
3. **Live Updates**: Adjust interval in `app.js`
4. **Rate Limiting**: Modify in `backend/app/main.py`

---

## 🔐 Security Notes

### ⚠️ Production Considerations
- ✅ Backend uses rate limiting (1 req/sec per IP)
- ✅ CORS should be configured before production
- ✅ API authentication recommended for production
- ✅ HTTPS required for sensitive data
- ✅ Input validation on all endpoints

### Current Development Status
🔨 This is a **development dashboard**  
⚠️ Not for production use without hardening  
🔒 Add authentication before deploying  

---

## 📚 File Structure

```
OSIN/
├── frontend/
│   ├── index.html           # Dashboard UI
│   ├── app.js               # Dashboard logic
│   └── style.css            # Styling
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app
│   │   ├── config.py        # Settings
│   │   ├── api/
│   │   │   └── router.py    # API endpoints
│   │   └── ...
│   └── requirements.txt
├── launch_dashboards.py     # Python launcher
└── launch_dashboards.bat    # Batch launcher
```

---

## 🚀 Deployment

### Local Development
```powershell
python launch_dashboards.py
# Dashboard opens automatically at http://localhost:8000
```

### Docker Deployment
```bash
docker-compose up -d
# Dashboard at http://localhost:8000
```

### Production Deployment
See `deployment/` directory for production configurations.

---

## 📞 Support

### Getting Help
1. Check the **Logs**: Terminal output from backend
2. Use **Browser DevTools**: F12 for client errors
3. Test **API Directly**: Use `/docs` at http://localhost:8000/docs
4. Review **Configuration**: Check `config.py` settings

### Quick Commands
```powershell
# Start dashboard
python launch_dashboards.py

# Test API
Invoke-WebRequest http://localhost:8000/health

# Stop dashboard
Ctrl+C (in terminal)
```

---

## ✨ Features Coming Soon

- 📊 **Real Database Integration** - Replace mock data
- 🔐 **Authentication & Roles** - Secure access control
- 📈 **Advanced Analytics** - Detailed breakdowns
- 🌍 **Global Map View** - Geospatial intelligence
- 🔔 **Alerts & Notifications** - Real-time alerts
- 📱 **Mobile Dashboard** - Responsive mobile UI

---

**Dashboard Version**: 1.0  
**Last Updated**: 2025-04-05  
**Status**: ✅ Production Ready for Development
