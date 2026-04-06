/* OSIN 3D DASHBOARD - COMPLETE COMPONENT BUNDLE
   This file contains all source code needed for the React dashboard
   Copy each section to the appropriate file in the dashboard/src directory
*/

// ============================================
// FILE: src/types/index.ts
// ============================================

export interface IntelligenceEvent {
  id: string;
  platform: 'twitter' | 'reddit' | 'youtube' | 'news';
  text: string;
  confidence: number;
  timestamp: string;
  location?: {
    lat: number;
    lon: number;
    accuracy?: number;
  };
  entities?: string[];
  sourceUrl?: string;
  mediaType?: string;
  rawData?: any;
}

export interface Alert {
  id: string;
  priority: 'high' | 'medium' | 'low';
  message: string;
  timestamp: string;
  eventId?: string;
  acknowledged: boolean;
  source?: string;
}

export interface SourceStats {
  twitter: number;
  reddit: number;
  youtube: number;
  news: number;
  total: number;
}

export interface WebSocketMessage {
  type: 'event' | 'alert' | 'stats' | 'threat' | 'ack';
  payload: any;
}


// ============================================
// FILE: src/store/useStore.ts
// ============================================

import { create } from 'zustand';
import { IntelligenceEvent, Alert, SourceStats } from '../types';

interface StoreState {
  events: IntelligenceEvent[];
  alerts: Alert[];
  sourceStats: SourceStats;
  threatLevel: number;
  addEvent: (event: IntelligenceEvent) => void;
  addAlert: (alert: Alert) => void;
  updateSourceStats: (stats: Partial<SourceStats>) => void;
  updateThreatLevel: (level: number) => void;
  clearAlerts: () => void;
}

export const useStore = create<StoreState>((set) => ({
  events: [],
  alerts: [],
  sourceStats: {
    twitter: 0,
    reddit: 0,
    youtube: 0,
    news: 0,
    total: 0
  },
  threatLevel: 0,
  
  addEvent: (event) => set((state) => ({
    events: [event, ...state.events.slice(0, 99)]
  })),
  
  addAlert: (alert) => set((state) => ({
    alerts: [alert, ...state.alerts.slice(0, 19)]
  })),
  
  updateSourceStats: (newStats) => set((state) => ({
    sourceStats: { ...state.sourceStats, ...newStats }
  })),
  
  updateThreatLevel: (level) => set({ threatLevel: level }),
  
  clearAlerts: () => set({ alerts: [] })
}));


// ============================================
// FILE: src/hooks/useWebSocket.ts
// ============================================

import { useEffect } from 'react';
import { useStore } from '../store/useStore';
import { WebSocketMessage } from '../types';

export const useWebSocket = () => {
  const { addEvent, addAlert, updateSourceStats, updateThreatLevel } = useStore();

  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const host = window.location.hostname;
    const port = window.location.port ? `:${window.location.port}` : '';
    const wsUrl = `${protocol}://${host}${port}/ws/intelligence`;

    console.log('Connecting to WebSocket:', wsUrl);

    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      try {
        const data: WebSocketMessage = JSON.parse(event.data);
        
        switch (data.type) {
          case 'event':
            addEvent(data.payload);
            break;
          case 'alert':
            addAlert(data.payload);
            break;
          case 'stats':
            updateSourceStats(data.payload);
            break;
          case 'threat':
            updateThreatLevel(data.payload.level);
            break;
          case 'ack':
            console.log('Server acknowledged:', data.payload);
            break;
          default:
            console.log('Unknown message type:', data.type);
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket connection closed. Reconnecting in 3 seconds...');
      setTimeout(() => {
        window.location.reload();
      }, 3000);
    };

    return () => {
      ws.close();
    };
  }, [addEvent, addAlert, updateSourceStats, updateThreatLevel]);
};


// ============================================
// FILE: src/components/Globe.tsx
// ============================================

import React, { useRef, useEffect } from 'react';
import Globe from 'react-globe.gl';
import { IntelligenceEvent } from '../types';

interface GlobeProps {
  events: IntelligenceEvent[];
}

export const GlobeComponent: React.FC<GlobeProps> = ({ events }) => {
  const globeRef = useRef<any>();
  
  const getGlobeData = () => {
    return events
      .filter(event => event.location && event.location.lat && event.location.lon)
      .map(event => ({
        lat: event.location!.lat,
        lng: event.location!.lon,
        radius: 0.1 + (event.confidence * 0.4),
        color: getColorByConfidence(event.confidence),
        ...event
      }));
  };

  const getColorByConfidence = (confidence: number): string => {
    if (confidence > 0.8) return '#ff0000';
    if (confidence > 0.6) return '#ff9900';
    if (confidence > 0.4) return '#ffff00';
    return '#00ff00';
  };

  useEffect(() => {
    if (globeRef.current) {
      globeRef.current.controls().autoRotate = true;
      globeRef.current.controls().autoRotateSpeed = 0.5;
    }
  }, []);

  return (
    <div style={{ width: '100%', height: '100%' }}>
      <Globe
        ref={globeRef}
        globeImageUrl="//unpkg.com/three-globe/example/img/earth-blue-marble.jpg"
        backgroundImageUrl="//unpkg.com/three-globe/example/img/night-sky.png"
        pointsData={getGlobeData()}
        pointAltitude="radius"
        pointColor="color"
        pointRadius={0.25}
        pointResolution={8}
      />
    </div>
  );
};


// ============================================
// FILE: src/components/ThreatBar.tsx
// ============================================

import React from 'react';
import '../styles/threat-bar.css';

interface ThreatBarProps {
  level: number;
}

export const ThreatBar: React.FC<ThreatBarProps> = ({ level }) => {
  const getThreatLevelText = (level: number): string => {
    if (level >= 80) return 'CRITICAL';
    if (level >= 60) return 'HIGH';
    if (level >= 40) return 'ELEVATED';
    if (level >= 20) return 'GUARDED';
    return 'LOW';
  };

  const getThreatColor = (level: number): string => {
    if (level >= 80) return '#ff0000';
    if (level >= 60) return '#ff5500';
    if (level >= 40) return '#ffaa00';
    if (level >= 20) return '#ffff00';
    return '#00ff00';
  };

  return (
    <div className="threat-bar-container">
      <div className="threat-level-text">
        THREAT LEVEL: <span style={{ color: getThreatColor(level) }}>
          {getThreatLevelText(level)}
        </span>
      </div>
      
      <div className="threat-bar">
        <div 
          className="threat-progress"
          style={{
            width: `${level}%`,
            backgroundColor: getThreatColor(level)
          }}
        />
      </div>
      
      <div className="threat-metrics">
        <div className="metric">
          <span className="metric-label">Active Events:</span>
          <span className="metric-value">{Math.ceil(level / 10)}</span>
        </div>
        <div className="metric">
          <span className="metric-label">Confidence:</span>
          <span className="metric-value">{level}%</span>
        </div>
      </div>
    </div>
  );
};


// ============================================
// FILE: src/components/SourcePanel.tsx
// ============================================

import React from 'react';
import { SourceStats } from '../types';
import '../styles/source-panel.css';

interface SourcePanelProps {
  stats: SourceStats;
}

export const SourcePanel: React.FC<SourcePanelProps> = ({ stats }) => {
  const sources = [
    { name: 'Twitter', key: 'twitter', count: stats.twitter, color: '#1DA1F2' },
    { name: 'Reddit', key: 'reddit', count: stats.reddit, color: '#FF5700' },
    { name: 'YouTube', key: 'youtube', count: stats.youtube, color: '#FF0000' },
    { name: 'News', key: 'news', count: stats.news, color: '#0088CC' }
  ];

  return (
    <div className="source-panel-container">
      {sources.map((source) => (
        <div key={source.key} className="source-item">
          <div className="source-header">
            <span 
              className="source-color" 
              style={{ backgroundColor: source.color }}
            />
            <span className="source-name">{source.name}</span>
            <span className="source-count">{source.count}</span>
          </div>
          <div className="source-bar">
            <div 
              className="source-progress"
              style={{
                width: `${(source.count / Math.max(1, stats.total)) * 100}%`,
                backgroundColor: source.color
              }}
            />
          </div>
        </div>
      ))}
      
      <div className="source-total">
        <span>Total Events:</span>
        <span className="total-count">{stats.total}</span>
      </div>
    </div>
  );
};


// ============================================
// FILE: src/components/LiveFeed.tsx
// ============================================

import React from 'react';
import { IntelligenceEvent } from '../types';
import '../styles/live-feed.css';

interface LiveFeedProps {
  events: IntelligenceEvent[];
}

export const LiveFeed: React.FC<LiveFeedProps> = ({ events }) => {
  const getPlatformIcon = (platform: string): string => {
    switch (platform) {
      case 'twitter': return '🐦';
      case 'reddit': return '👾';
      case 'youtube': return '🎥';
      case 'news': return '📰';
      default: return '🔍';
    }
  };

  const getConfidenceColor = (confidence: number): string => {
    if (confidence > 0.8) return '#ff0000';
    if (confidence > 0.6) return '#ffaa00';
    if (confidence > 0.4) return '#00ff00';
    return '#888888';
  };

  return (
    <div className="live-feed-container">
      {events.length === 0 ? (
        <div className="no-events">Loading intelligence feed...</div>
      ) : (
        events.slice(0, 20).map((event, index) => (
          <div key={`${event.id}-${index}`} className="event-item">
            <div className="event-header">
              <span className="event-platform">
                {getPlatformIcon(event.platform)} {event.platform.toUpperCase()}
              </span>
              <span 
                className="event-confidence"
                style={{ color: getConfidenceColor(event.confidence) }}
              >
                {Math.round(event.confidence * 100)}%
              </span>
            </div>
            
            <div className="event-content">
              {event.text}
            </div>
            
            <div className="event-footer">
              <span className="event-time">
                {new Date(event.timestamp).toLocaleTimeString()}
              </span>
              {event.location && (
                <span className="event-location">
                  📍 {event.location.lat.toFixed(2)}, {event.location.lon.toFixed(2)}
                </span>
              )}
            </div>
          </div>
        ))
      )}
    </div>
  );
};


// ============================================
// FILE: src/components/Alerts.tsx
// ============================================

import React from 'react';
import { Alert } from '../types';
import '../styles/alerts.css';

interface AlertsProps {
  alerts: Alert[];
}

export const Alerts: React.FC<AlertsProps> = ({ alerts }) => {
  const getPriorityIcon = (priority: string): string => {
    switch (priority) {
      case 'high': return '🔴';
      case 'medium': return '🟡';
      case 'low': return '🔵';
      default: return '⚪';
    }
  };

  return (
    <div className="alerts-container">
      {alerts.length === 0 ? (
        <div className="no-alerts">
          <div className="no-alerts-icon">✅</div>
          <div className="no-alerts-text">No active alerts</div>
        </div>
      ) : (
        alerts.map((alert) => (
          <div key={alert.id} className={`alert-item ${alert.priority}`}>
            <div className="alert-header">
              <span className="alert-priority">
                {getPriorityIcon(alert.priority)} {alert.priority.toUpperCase()}
              </span>
              <span className="alert-time">
                {new Date(alert.timestamp).toLocaleTimeString()}
              </span>
            </div>
            
            <div className="alert-message">
              {alert.message}
            </div>
            
            {alert.source && (
              <div className="alert-source">
                Source: {alert.source}
              </div>
            )}
          </div>
        ))
      )}
    </div>
  );
};


// ============================================
// FILE: src/App.tsx
// ============================================

import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { GlobeComponent } from './components/Globe';
import { ThreatBar } from './components/ThreatBar';
import { SourcePanel } from './components/SourcePanel';
import { LiveFeed } from './components/LiveFeed';
import { Alerts } from './components/Alerts';
import { useWebSocket } from './hooks/useWebSocket';
import { useStore } from './store/useStore';
import './App.css';

const Dashboard: React.FC = () => {
  const { events, alerts, sourceStats, threatLevel } = useStore();
  
  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>OSIN TACTICAL INTELLIGENCE</h1>
        <div className="status-indicator">
          <span className="status-dot live"></span>
          LIVE
        </div>
      </header>

      <div className="dashboard-grid">
        <div className="panel live-feed-panel">
          <h2>LIVE INTELLIGENCE FEED</h2>
          <LiveFeed events={events} />
        </div>

        <div className="panel alerts-panel">
          <h2>ALERTS</h2>
          <Alerts alerts={alerts} />
        </div>

        <div className="panel globe-panel">
          <h2>3D GLOBAL INTELLIGENCE MAP</h2>
          <GlobeComponent events={events} />
        </div>

        <div className="panel source-panel">
          <h2>SOURCES</h2>
          <SourcePanel stats={sourceStats} />
        </div>

        <div className="panel threat-panel">
          <h2>THREAT ASSESSMENT</h2>
          <ThreatBar level={threatLevel} />
        </div>
      </div>
    </div>
  );
};

const Nav: React.FC = () => (
  <nav className="navigation">
    <div className="nav-brand">
      <h2>OSIN</h2>
      <span className="status-dot live"></span>
    </div>
    <div className="nav-links">
      <Link to="/" className="nav-link">
        Dashboard
      </Link>
      <Link to="/" className="nav-link" onClick={() => window.open('file:///C:/Users/User/Documents/OSIN/frontend/index.html', '_blank')}>
        Terminal
      </Link>
      <Link to="/analytics" className="nav-link">
        Analytics
      </Link>
    </div>
    <div className="nav-time">
      {new Date().toLocaleTimeString()}
    </div>
  </nav>
);

const App: React.FC = () => {
  useWebSocket();

  return (
    <Router>
      <div className="app-container">
        <Nav />
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/analytics" element={<div className="analytics-page">Analytics Dashboard - Coming Soon</div>} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;


// ============================================
// FILE: src/main.tsx
// ============================================

import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './App.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)


// ============================================
// FILE: index.html
// ============================================

/*
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>OSIN 3D Intelligence Dashboard</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
*/
