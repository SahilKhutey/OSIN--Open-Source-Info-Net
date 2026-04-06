# OSIN 3D Dashboard Architecture

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          WEB BROWSER                             │
│                   (http://localhost:5173)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────────── REACT 3D DASHBOARD ─────────────────┐  │
│  │                                                             │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │              DASHBOARD MAIN LAYOUT                   │  │  │
│  │  │                                                       │  │  │
│  │  │  ┌──────────────────┐ ┌──────────────────────────┐  │  │  │
│  │  │  │  3D GLOBE        │ │  RIGHT SIDEBAR           │  │  │  │
│  │  │  │  (or Heatmap)    │ │                          │  │  │  │
│  │  │  │                  │ │  ┌──────────────────────┐ │  │  │
│  │  │  │  - Events        │ │  │  LIVE FEED          │ │  │  │
│  │  │  │  - Severity      │ │  │  (Latest 10)        │ │  │  │
│  │  │  │  - Locations     │ │  │                      │ │  │  │
│  │  │  │  - Legend        │ │  └──────────────────────┘ │  │  │
│  │  │  │                  │ │                          │  │  │
│  │  │  │                  │ │  ┌──────────────────────┐ │  │  │
│  │  │  │                  │ │  │  ALERTS             │ │  │  │
│  │  │  │  [MODE TOGGLE]   │ │  │  (Up to 20)         │ │  │  │
│  │  │  │  3D | HEATMAP    │ │  │                      │ │  │  │
│  │  │  │                  │ │  └──────────────────────┘ │  │  │
│  │  │  │                  │ │                          │  │  │
│  │  │  └──────────────────┘ │  ┌──────────────────────┐ │  │  │
│  │  │                        │  │ SOURCES PANEL       │ │  │  │
│  │  │                        │  │ - Twitter           │ │  │  │
│  │  │                        │  │ - Reddit            │ │  │  │
│  │  │                        │  │ - YouTube           │ │  │  │
│  │  │                        │  │ - News              │ │  │  │
│  │  │                        │  │ - Instagram         │ │  │  │
│  │  │                        │  │ - LinkedIn          │ │  │  │
│  │  │                        │  └──────────────────────┘ │  │  │
│  │  │                        │                          │  │  │
│  │  │                        │  ┌──────────────────────┐ │  │  │
│  │  │                        │  │ THREAT LEVEL        │ │  │  │
│  │  │                        │  │ GREEN/YEL/ORG/RED   │ │  │  │
│  │  │                        │  │ 0-100%              │ │  │  │
│  │  │                        │  └──────────────────────┘ │  │  │
│  │  │                        │                          │  │  │
│  │  │                        └──────────────────────────┘  │  │
│  │  │                                                       │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                                                             │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │          STATE MANAGEMENT (Zustand)                 │  │  │
│  │  │  ├─ events[]          (Max 100)                    │  │  │
│  │  │  ├─ alerts[]          (Max 20)                     │  │  │
│  │  │  ├─ sourceStats       (6 sources)                  │  │  │
│  │  │  ├─ threatLevel       (0-100%)                     │  │  │
│  │  │  └─ agentStatus       (AI agents)                  │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                                                             │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │       WEBSOCKET SERVICE (Auto-reconnecting)         │  │  │
│  │  │  Connect: ws://localhost:8000/ws/intelligence       │  │  │
│  │  │  ├─ Event messages       → addEvent()              │  │  │
│  │  │  ├─ Alert messages       → addAlert()              │  │  │
│  │  │  ├─ Stats messages       → updateSourceStats()     │  │  │
│  │  │  └─ Threat messages      → updateThreatLevel()     │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                                                             │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↕ WebSocket
                         (JSON Messages)
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND API SERVER                            │
│              (FastAPI on http://localhost:8000)                  │
├─────────────────────────────────────────────────────────────────┤
│  ├─ /api/events        (REST endpoints)                         │
│  ├─ /api/alerts                                                 │
│  ├─ /ws/intelligence   (WebSocket streaming)                    │
│  ├─ /docs              (API documentation)                      │
│  └─ /health            (Health check)                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧩 Component Tree

```
App
├── Dashboard
│   ├── Header
│   │   ├── Title
│   │   └── Mode Toggle (3D / Heatmap)
│   │
│   ├── Main Grid Layout
│   │   ├── Map Section (Left, Full Height)
│   │   │   ├── EnhancedGlobe (3D Mode)
│   │   │   │   ├── Globe (React-Globe.gl)
│   │   │   │   ├── Header Info
│   │   │   │   └── Legend
│   │   │   │
│   │   │   └── HeatmapGlobe (Heatmap Mode)
│   │   │       ├── Globe (Hex Binning)
│   │   │       ├── Header Info
│   │   │       └── Intensity Scale
│   │   │
│   │   ├── Left Sidebar (Top Right, Full Height)
│   │   │   ├── LiveFeed
│   │   │   │   ├── Header
│   │   │   │   └── Feed Items
│   │   │   │       └── EventCard (repeating)
│   │   │   │
│   │   │   └── Alerts
│   │   │       ├── Header
│   │   │       └── Alert Items
│   │   │           └── AlertCard (repeating)
│   │   │
│   │   └── Right Sidebar (Bottom Right)
│   │       ├── SourcePanel
│   │       │   ├── Header
│   │       │   ├── Source Grid
│   │       │   │   └── SourceItem (x6)
│   │       │   │       ├── Name
│   │       │   │       ├── Count
│   │       │   │       ├── Progress Bar
│   │       │   │       └── Percentage
│   │       │   └── Footer
│   │       │
│   │       └── ThreatBar
│   │           ├── Header
│   │           ├── Threat Level Bar
│   │           └── Status Text
│   │
│   └── WebSocket Connection (useWebSocket hook)
│       └── webSocketService
│           └── Auto-reconnect logic
```

---

## 📊 Data Flow Diagram

```
┌──────────────────┐
│  WEBSOCKET MSG   │
│  (JSON Format)   │
└────────┬─────────┘
         │
         ↓
┌────────────────────────────┐
│  WebSocket Service         │
│  (websocketService.ts)     │
│  ├─ Parse JSON            │
│  ├─ Route by type         │
│  └─ Call store actions    │
└────────┬───────────────────┘
         │
    ┌────┴─────────────────────────┐
    │                              │
    ↓                              ↓
┌─────────────────┐        ┌──────────────────┐
│ addEvent()      │        │ addAlert()       │
└────────┬────────┘        └────────┬─────────┘
         │                          │
         ↓                          ↓
    ┌────────────────────────────────────┐
    │  Zustand Store (useStore)          │
    │  ├─ events (max 100)              │
    │  ├─ alerts (max 20)               │
    │  ├─ sourceStats                   │
    │  ├─ threatLevel                   │
    │  └─ agentStatus                   │
    └────────┬──────────────────────────┘
             │
    ┌────────┴──────────────────────┐
    │                               │
    ↓                               ↓
┌──────────────┐            ┌─────────────────┐
│  Components  │            │   Components    │
│  Subscribe   │            │   Subscribe     │
└──────┬───────┘            └────────┬────────┘
       │                             │
    ┌──┴──┬────┬────┐               │
    ↓     ↓    ↓    ↓               ↓
┌─────────────────────────┐  ┌─────────────────┐
│ EnhancedGlobe           │  │ SourcePanel     │
│ ├─ Uses: events[]       │  │ ├─ Uses: stats  │
│ ├─ Maps to globe points │  │ └─ Shows bars   │
│ └─ Color by severity    │  └─────────────────┘
└─────────────────────────┘

│ LiveFeed                │  │ ThreatBar       │
│ ├─ Uses: events[]       │  │ ├─ Uses: level  │
│ ├─ Shows 10 newest      │  │ └─ Shows meter  │
│ └─ Sortable             │  └─────────────────┘
└─────────────────────────┘

│ Alerts                  │  │ HeatmapGlobe    │
│ ├─ Uses: alerts[]       │  │ ├─ Uses: events │
│ ├─ Shows active         │  │ ├─ Aggregates   │
│ └─ ACK system           │  │ └─ Hex bins     │
└─────────────────────────┘  └─────────────────┘
```

---

## 🔄 Message Flow Example

### Example: Event Arrives from Backend

```
1. BACKEND SENDS
   {
     "type": "event",
     "payload": {
       "id": "evt-123",
       "content": "Security threat detected",
       "severity": "high",
       "location": {"lat": 40.7128, "lng": -74.0060},
       ...
     }
   }

2. WEBSOCKET SERVICE RECEIVES
   websocketService.onmessage()
   ├─ Parse JSON
   ├─ Check type === "event"
   └─ Call addEvent(payload)

3. STORE UPDATES
   useStore.addEvent(payload)
   ├─ Prepend to events[]
   ├─ Keep max 100 items
   └─ Trigger re-render

4. COMPONENTS AUTO-UPDATE
   ├─ EnhancedGlobe
   │  ├─ Subscribes to events
   │  ├─ Converts to globe points
   │  └─ Adds new point at location
   │
   ├─ LiveFeed
   │  ├─ Subscribes to events
   │  ├─ Shows in feed
   │  └─ Updates count
   │
   └─ HeatmapGlobe
      ├─ Subscribes to events
      ├─ Aggregates by location
      └─ Updates hex bins

5. UI RENDERS
   ✅ Globe shows new event at (40.7128, -74.0060)
   ✅ Feed shows new item
   ✅ Heatmap updates intensity
   ✅ All in real-time!
```

---

## 🎨 Color Flow

```
WEBSOCKET DATA
    ↓
SEVERITY FIELD
    ├─ "critical" → 🔴 #ff0000 (Red)
    ├─ "high"     → 🟠 #ff6600 (Orange)
    ├─ "medium"   → 🟡 #ffff00 (Yellow)
    └─ "low"      → 🟢 #00ff00 (Green)
    ↓
APPLIED TO:
├─ Globe point color
├─ Feed item border
├─ Alert badge
├─ Threat bar fill
└─ HeatmapGlobe hex color
```

---

## 📱 Responsive Layout

```
DESKTOP (1400px+)
┌──────────────────────┬────────┐
│                      │ Feed   │
│                      │ Alerts │
│  3D GLOBE            ├────────┤
│  (Full Height)       │Sources │
│                      │Threat  │
└──────────────────────┴────────┘

TABLET (768px - 1200px)
┌────────────────────────────────┐
│         3D GLOBE               │
│      (400px height)            │
├──────────────────────────────────┤
│  Feed    │  Alerts              │
├──────────────────────────────────┤
│  Sources │  Threat              │
└────────────────────────────────┘

MOBILE (< 768px)
┌────────────────────┐
│   3D GLOBE         │
│ (scrollable area)  │
├────────────────────┤
│   LIVE FEED        │
│ (scrollable)       │
├────────────────────┤
│   ALERTS           │
│ (scrollable)       │
├────────────────────┤
│   SOURCES          │
│ (scrollable)       │
├────────────────────┤
│   THREAT LEVEL     │
└────────────────────┘
```

---

## 🔐 Type Safety Flow

```
WebSocket Message
    ↓
Message Type Check
    ├─ "event" → IntelligenceEvent
    ├─ "alert" → Alert
    ├─ "stats" → SourceStats
    └─ "threat" → { level: number }
    ↓
Type-Safe Store Action
    ├─ addEvent(event: IntelligenceEvent)
    ├─ addAlert(alert: Alert)
    ├─ updateSourceStats(stats: Partial<SourceStats>)
    └─ updateThreatLevel(level: number)
    ↓
Type-Safe Components
    ├─ EnhancedGlobe<React.FC>
    ├─ LiveFeed<React.FC>
    ├─ Alerts<React.FC>
    └─ (All receive type-safe props)
    ↓
Type-Safe Props
    ├─ useStore hooks typed
    ├─ Callbacks typed
    └─ Event handlers typed
```

---

## 🚀 Startup Sequence

```
1. npm run dev
   └─ Vite dev server starts on :5173

2. React App Mounts
   ├─ index.tsx runs
   ├─ <App> component loads
   └─ useEffect triggers

3. WebSocket Connection Initiates
   ├─ useWebSocket hook
   ├─ websocketService.connect()
   ├─ ws://localhost:8000/ws/intelligence
   └─ Awaits connection

4. Dashboard Renders
   ├─ <Dashboard> component
   ├─ <EnhancedGlobe> loads
   ├─ <SourcePanel> initializes
   └─ UI ready (but empty)

5. Live Data Begins
   ├─ Backend sends messages
   ├─ WebSocket receives
   ├─ Store updates
   └─ Components re-render
   
6. User Interaction
   ├─ Click globe point
   ├─ Toggle 3D/Heatmap
   ├─ Acknowledge alerts
   └─ Monitor real-time
```

---

## ✨ This Architecture Provides

✅ **Real-time Updates** - WebSocket streaming  
✅ **Type Safety** - Full TypeScript coverage  
✅ **Scalability** - Component-based design  
✅ **Performance** - Efficient state management  
✅ **Maintainability** - Clear separation of concerns  
✅ **Responsiveness** - Mobile-friendly layout  
✅ **Extensibility** - Easy to add new components  
✅ **Error Handling** - Auto-reconnecting WebSocket  

---

🎉 **Complete, Production-Ready Architecture!**
