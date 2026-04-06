# OSIN React Dashboard - Component Files

## File: src/types/index.ts

```typescript
export interface IntelligenceEvent {
  id: string;
  platform: string;
  text: string;
  confidence: number;
  timestamp: string;
  location?: {
    lat: number;
    lon: number;
    accuracy?: number;
    city?: string;
    country?: string;
  };
  entities?: string[];
  sourceUrl?: string;
  mediaType?: 'text' | 'image' | 'video' | 'audio';
  engagement?: {
    likes?: number;
    shares?: number;
    comments?: number;
    views?: number;
  };
  rawData?: any;
  metadata?: {
    language?: string;
    sentiment?: number;
    category?: string;
    author?: string;
  };
}

export interface Alert {
  id: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  message: string;
  timestamp: string;
  eventId?: string;
  acknowledged: boolean;
  source?: string;
  actions?: AlertAction[];
  metadata?: {
    triggeredBy?: string;
    confidence?: number;
    relatedEvents?: string[];
  };
}

export interface AlertAction {
  id: string;
  label: string;
  type: 'acknowledge' | 'dismiss' | 'escalate';
  handler: () => void;
}

export interface SourceStats {
  twitter: number;
  reddit: number;
  youtube: number;
  news: number;
  telegram?: number;
  instagram?: number;
  linkedin?: number;
  total: number;
  lastUpdated: string;
  trends?: SourceTrend[];
}

export interface SourceTrend {
  platform: string;
  change: number;
  direction: 'up' | 'down' | 'stable';
}

export interface ThreatLevel {
  value: number;
  level: 'critical' | 'high' | 'elevated' | 'guarded' | 'low';
  trend: 'increasing' | 'decreasing' | 'stable';
  factors: ThreatFactor[];
  timestamp: string;
}

export interface ThreatFactor {
  type: 'volume' | 'confidence' | 'velocity' | 'diversity';
  score: number;
  description: string;
}
```

---

## File: src/store/useStore.ts

```typescript
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
  acknowledgeAlert: (id: string) => void;
}

export const useStore = create<StoreState>((set) => ({
  events: [],
  alerts: [],
  sourceStats: {
    twitter: 0,
    reddit: 0,
    youtube: 0,
    news: 0,
    total: 0,
    lastUpdated: new Date().toISOString()
  },
  threatLevel: 0,

  addEvent: (event) =>
    set((state) => ({
      events: [event, ...state.events.slice(0, 99)]
    })),

  addAlert: (alert) =>
    set((state) => ({
      alerts: [alert, ...state.alerts.slice(0, 19)]
    })),

  updateSourceStats: (newStats) =>
    set((state) => ({
      sourceStats: {
        ...state.sourceStats,
        ...newStats,
        lastUpdated: new Date().toISOString()
      }
    })),

  updateThreatLevel: (level) => set({ threatLevel: level }),

  clearAlerts: () => set({ alerts: [] }),

  acknowledgeAlert: (id) =>
    set((state) => ({
      alerts: state.alerts.map((alert) =>
        alert.id === id ? { ...alert, acknowledged: true } : alert
      )
    }))
}));
```

---

## File: src/hooks/useWebSocket.ts

```typescript
import { useEffect } from 'react';
import { useStore } from '../store/useStore';
import { IntelligenceEvent, Alert } from '../types';

export const useWebSocket = () => {
  const { addEvent, addAlert, updateSourceStats, updateThreatLevel } = useStore();

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/intelligence');

    ws.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        switch (data.type) {
          case 'event':
            addEvent(data.payload as IntelligenceEvent);
            break;
          case 'alert':
            addAlert(data.payload as Alert);
            break;
          case 'stats':
            updateSourceStats(data.payload);
            break;
          case 'threat':
            updateThreatLevel(data.payload.level);
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
      console.log('WebSocket closed. Reconnecting in 3 seconds...');
      setTimeout(() => {
        window.location.reload();
      }, 3000);
    };

    return () => {
      ws.close();
    };
  }, [addEvent, addAlert, updateSourceStats, updateThreatLevel]);
};
```

---

## File: src/components/EnhancedGlobe.tsx

```typescript
import React, { useRef, useEffect, useState } from 'react';
import Globe from 'react-globe.gl';
import * as THREE from 'three';
import { IntelligenceEvent } from '../types';

interface EnhancedGlobeProps {
  events: IntelligenceEvent[];
  onEventClick?: (event: IntelligenceEvent) => void;
  focusPoint?: { lat: number; lng: number; altitude?: number };
  autoRotate?: boolean;
}

export const EnhancedGlobe: React.FC<EnhancedGlobeProps> = ({
  events,
  onEventClick,
  focusPoint,
  autoRotate = true
}) => {
  const globeRef = useRef<any>();
  const [globeReady, setGlobeReady] = useState(false);

  const getGlobeData = () => {
    return events
      .filter(event => event.location && event.location.lat && event.location.lon)
      .map(event => ({
        lat: event.location!.lat,
        lng: event.location!.lon,
        radius: 0.1 + (event.confidence * 0.4),
        color: getColorByConfidence(event.confidence),
        altitude: Math.random() * 0.1,
        event: event
      }));
  };

  const getColorByConfidence = (confidence: number): string => {
    if (confidence > 0.8) return '#ff0000';
    if (confidence > 0.6) return '#ff5500';
    if (confidence > 0.4) return '#ffaa00';
    if (confidence > 0.2) return '#ffff00';
    return '#00ff00';
  };

  useEffect(() => {
    if (globeRef.current && !globeReady) {
      if (autoRotate) {
        globeRef.current.controls().autoRotate = true;
        globeRef.current.controls().autoRotateSpeed = 0.5;
      }

      const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
      globeRef.current.scene().add(ambientLight);

      setGlobeReady(true);
    }
  }, [autoRotate, globeReady]);

  useEffect(() => {
    if (globeRef.current && focusPoint) {
      globeRef.current.pointOfView({
        lat: focusPoint.lat,
        lng: focusPoint.lng,
        altitude: focusPoint.altitude || 1.5
      }, 2000);
    }
  }, [focusPoint]);

  return (
    <div className="globe-container">
      <Globe
        ref={globeRef}
        globeImageUrl="//unpkg.com/three-globe/example/img/earth-blue-marble.jpg"
        backgroundImageUrl="//unpkg.com/three-globe/example/img/night-sky.png"
        pointsData={getGlobeData()}
        pointAltitude="altitude"
        pointColor="color"
        pointRadius={(d: any) => d.radius}
        pointResolution={12}
        onPointClick={(point: any) => {
          if (onEventClick && point.event) {
            onEventClick(point.event);
          }
        }}
        rendererConfig={{ antialias: true, alpha: true }}
        animateIn={true}
      />
    </div>
  );
};
```

---

## File: src/components/ThreatBar.tsx

```typescript
import React from 'react';

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
        THREAT LEVEL:{' '}
        <span style={{ color: getThreatColor(level) }}>
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
          <span className="metric-value">{Math.round(level / 10)}</span>
        </div>
        <div className="metric">
          <span className="metric-label">Confidence:</span>
          <span className="metric-value">{level}%</span>
        </div>
      </div>
    </div>
  );
};
```

---

## File: src/components/SourcePanel.tsx

```typescript
import React from 'react';
import { SourceStats } from '../types';

interface SourcePanelProps {
  stats: SourceStats;
}

export const SourcePanel: React.FC<SourcePanelProps> = ({ stats }) => {
  const sources = [
    { name: 'Twitter', count: stats.twitter, color: '#1DA1F2' },
    { name: 'Reddit', count: stats.reddit, color: '#FF5700' },
    { name: 'YouTube', count: stats.youtube, color: '#FF0000' },
    { name: 'News', count: stats.news, color: '#0088CC' }
  ];

  return (
    <div className="source-panel-container">
      {sources.map((source) => (
        <div key={source.name} className="source-item">
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
        <span>Total Sources:</span>
        <span className="total-count">{stats.total}</span>
      </div>
    </div>
  );
};
```

---

## File: src/components/LiveFeed.tsx

```typescript
import React from 'react';
import { IntelligenceEvent } from '../types';

interface LiveFeedProps {
  events: IntelligenceEvent[];
  onEventClick?: (event: IntelligenceEvent) => void;
}

export const LiveFeed: React.FC<LiveFeedProps> = ({ events, onEventClick }) => {
  const getPlatformIcon = (platform: string): string => {
    switch (platform) {
      case 'twitter':
        return '🐦';
      case 'reddit':
        return '👾';
      case 'youtube':
        return '🎥';
      case 'news':
        return '📰';
      default:
        return '🔍';
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
        <div className="no-events">Waiting for live events...</div>
      ) : (
        events.slice(0, 20).map((event, index) => (
          <div
            key={`${event.id}-${index}`}
            className="event-item"
            onClick={() => onEventClick?.(event)}
            style={{ cursor: 'pointer' }}
          >
            <div className="event-header">
              <span className="event-platform">
                {getPlatformIcon(event.platform)} {event.platform.toUpperCase()}
              </span>
              <span className="event-confidence" style={{ color: getConfidenceColor(event.confidence) }}>
                {Math.round(event.confidence * 100)}%
              </span>
            </div>

            <div className="event-content">{event.text}</div>

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
```

---

## File: src/components/Alerts.tsx

```typescript
import React from 'react';
import { Alert } from '../types';
import { useStore } from '../store/useStore';

interface AlertsProps {
  alerts: Alert[];
}

export const Alerts: React.FC<AlertsProps> = ({ alerts }) => {
  const { acknowledgeAlert } = useStore();

  const getPriorityIcon = (priority: string): string => {
    switch (priority) {
      case 'critical':
        return '🔴';
      case 'high':
        return '🔴';
      case 'medium':
        return '🟡';
      case 'low':
        return '🔵';
      default:
        return '⚪';
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

            <div className="alert-message">{alert.message}</div>

            {alert.source && <div className="alert-source">Source: {alert.source}</div>}

            {!alert.acknowledged && (
              <button
                className="acknowledge-btn"
                onClick={() => acknowledgeAlert(alert.id)}
              >
                Acknowledge
              </button>
            )}
          </div>
        ))
      )}
    </div>
  );
};
```

---

## File: src/components/EventDetailModal.tsx

```typescript
import React from 'react';
import { IntelligenceEvent } from '../types';

interface EventDetailModalProps {
  event: IntelligenceEvent | null;
  onClose: () => void;
}

export const EventDetailModal: React.FC<EventDetailModalProps> = ({ event, onClose }) => {
  if (!event) return null;

  const getConfidenceLabel = (confidence: number): string => {
    if (confidence >= 0.9) return 'Very High';
    if (confidence >= 0.7) return 'High';
    if (confidence >= 0.5) return 'Medium';
    if (confidence >= 0.3) return 'Low';
    return 'Very Low';
  };

  const getPlatformIcon = (platform: string): string => {
    const icons: Record<string, string> = {
      twitter: '🐦',
      reddit: '👾',
      youtube: '🎥',
      news: '📰',
      instagram: '📸',
      linkedin: '💼',
      telegram: '📱'
    };
    return icons[platform] || '🌐';
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Event Details</h2>
          <button className="modal-close" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="modal-body">
          <div className="event-detail-section">
            <h3>Basic Information</h3>
            <div className="detail-item">
              <span className="detail-label">Platform:</span>
              <span className="detail-value">
                {getPlatformIcon(event.platform)} {event.platform}
              </span>
            </div>

            <div className="detail-item">
              <span className="detail-label">Timestamp:</span>
              <span className="detail-value">{new Date(event.timestamp).toLocaleString()}</span>
            </div>

            <div className="detail-item">
              <span className="detail-label">Confidence:</span>
              <span className="detail-value">
                {getConfidenceLabel(event.confidence)} ({Math.round(event.confidence * 100)}%)
              </span>
            </div>
          </div>

          {event.location && (
            <div className="event-detail-section">
              <h3>Location</h3>
              <div className="detail-item">
                <span className="detail-label">Coordinates:</span>
                <span className="detail-value">
                  {event.location.lat.toFixed(4)}, {event.location.lon.toFixed(4)}
                </span>
              </div>
            </div>
          )}

          <div className="event-detail-section">
            <h3>Content</h3>
            <div className="detail-item">
              <span className="detail-label">Text:</span>
              <div className="detail-value text-content">{event.text}</div>
            </div>
          </div>

          {event.entities && event.entities.length > 0 && (
            <div className="event-detail-section">
              <h3>Entities</h3>
              <div className="entities-list">
                {event.entities.map((entity, index) => (
                  <span key={index} className="entity-tag">
                    {entity}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button className="btn-secondary" onClick={onClose}>
            Close
          </button>
          {event.sourceUrl && (
            <a
              href={event.sourceUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-primary"
            >
              View Original
            </a>
          )}
        </div>
      </div>
    </div>
  );
};
```

---

## File: src/components/EnhancedTerminal.tsx

```typescript
import React, { useState, useRef, useEffect } from 'react';
import { useStore } from '../store/useStore';

interface TerminalCommand {
  id: string;
  command: string;
  timestamp: string;
  output?: string;
  isError?: boolean;
}

export const EnhancedTerminal: React.FC = () => {
  const [input, setInput] = useState('');
  const [history, setHistory] = useState<TerminalCommand[]>([]);
  const [commandHistory, setCommandHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const terminalRef = useRef<HTMLDivElement>(null);

  const { events, alerts } = useStore();

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }

    addOutput('OSIN Intelligence Terminal v2.0', false);
    addOutput('Type "help" for available commands', false);
  }, []);

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [history]);

  const addOutput = (text: string, isError: boolean = false) => {
    const newEntry: TerminalCommand = {
      id: `cmd-${Date.now()}`,
      command: '',
      timestamp: new Date().toISOString(),
      output: text,
      isError
    };
    setHistory((prev) => [...prev, newEntry]);
  };

  const executeCommand = (cmd: string) => {
    const trimmedCmd = cmd.trim().toLowerCase();

    if (trimmedCmd && !commandHistory.includes(trimmedCmd)) {
      setCommandHistory((prev) => [trimmedCmd, ...prev.slice(0, 49)]);
    }

    const newEntry: TerminalCommand = {
      id: `cmd-${Date.now()}`,
      command: cmd,
      timestamp: new Date().toISOString()
    };
    setHistory((prev) => [...prev, newEntry]);

    switch (trimmedCmd) {
      case '':
        break;
      case 'help':
        addOutput('Available commands:');
        addOutput('  help - Show this help');
        addOutput('  clear - Clear terminal');
        addOutput('  status - Show system status');
        addOutput('  events - Show recent events');
        addOutput('  alerts - Show recent alerts');
        break;
      case 'clear':
        setHistory([]);
        break;
      case 'status':
        addOutput('System Status:');
        addOutput(`  Events: ${events.length}`);
        addOutput(`  Alerts: ${alerts.length}`);
        addOutput('  Connection: Online');
        break;
      case 'events':
        addOutput(`Recent Events (${Math.min(5, events.length)} of ${events.length}):`);
        events.slice(0, 5).forEach((event) => {
          addOutput(`  [${event.platform}] ${event.text.substring(0, 60)}...`);
        });
        break;
      case 'alerts':
        addOutput(`Recent Alerts (${alerts.length}):`);
        alerts.slice(0, 5).forEach((alert) => {
          addOutput(`  [${alert.priority}] ${alert.message}`);
        });
        break;
      default:
        addOutput(`Command not found: ${cmd}`, true);
        addOutput('Type "help" for available commands', true);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    switch (e.key) {
      case 'Enter':
        if (input.trim()) {
          executeCommand(input);
          setInput('');
          setHistoryIndex(-1);
        }
        break;
      case 'ArrowUp':
        e.preventDefault();
        if (commandHistory.length > 0) {
          const newIndex = historyIndex < commandHistory.length - 1 ? historyIndex + 1 : 0;
          setHistoryIndex(newIndex);
          setInput(commandHistory[newIndex]);
        }
        break;
      case 'ArrowDown':
        e.preventDefault();
        if (historyIndex > 0) {
          const newIndex = historyIndex - 1;
          setHistoryIndex(newIndex);
          setInput(commandHistory[newIndex]);
        } else if (historyIndex === 0) {
          setHistoryIndex(-1);
          setInput('');
        }
        break;
    }
  };

  return (
    <div className="enhanced-terminal">
      <div className="terminal-header">
        <h2>OSIN COMMAND TERMINAL</h2>
        <div className="terminal-status">
          <span className="status-dot live"></span>
          ONLINE
        </div>
      </div>

      <div ref={terminalRef} className="terminal-output">
        {history.map((entry) => (
          <div key={entry.id} className={`terminal-line ${entry.isError ? 'error' : ''}`}>
            {entry.command && (
              <div className="command-line">
                <span className="prompt">{'>'}</span>
                <span className="command-text">{entry.command}</span>
              </div>
            )}
            {entry.output && <div className="output-line">{entry.output}</div>}
          </div>
        ))}
      </div>

      <div className="terminal-input-area">
        <span className="prompt">{'>'}</span>
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          className="terminal-input"
          placeholder="Enter command..."
        />
      </div>
    </div>
  );
};
```

---

## File: src/components/Dashboard.tsx

```typescript
import React, { useState } from 'react';
import { useStore } from '../store/useStore';
import { EnhancedGlobe } from './EnhancedGlobe';
import { ThreatBar } from './ThreatBar';
import { SourcePanel } from './SourcePanel';
import { LiveFeed } from './LiveFeed';
import { Alerts } from './Alerts';
import { EventDetailModal } from './EventDetailModal';
import { IntelligenceEvent } from '../types';

export const Dashboard: React.FC = () => {
  const { events, alerts, sourceStats, threatLevel } = useStore();
  const [selectedEvent, setSelectedEvent] = useState<IntelligenceEvent | null>(null);
  const [focusPoint, setFocusPoint] = useState<{ lat: number; lng: number } | null>(null);

  const handleEventClick = (event: IntelligenceEvent) => {
    setSelectedEvent(event);

    if (event.location) {
      setFocusPoint({
        lat: event.location.lat,
        lng: event.location.lon
      });
    }
  };

  const handleCloseModal = () => {
    setSelectedEvent(null);
    setFocusPoint(null);
  };

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
          <div className="panel-header">
            <h2 className="text-green-400">LIVE INTELLIGENCE FEED</h2>
            <div className="panel-controls">
              <span className="event-count">{events.length} events</span>
            </div>
          </div>
          <LiveFeed events={events} onEventClick={handleEventClick} />
        </div>

        <div className="panel alerts-panel">
          <div className="panel-header">
            <h2 className="text-red-400">ALERTS</h2>
            <div className="panel-controls">
              <span className="alert-count">
                {alerts.filter((a) => !a.acknowledged).length} active
              </span>
            </div>
          </div>
          <Alerts alerts={alerts} />
        </div>

        <div className="panel globe-panel">
          <div className="panel-header">
            <h2 className="text-blue-400">3D GLOBAL INTELLIGENCE MAP</h2>
            <div className="panel-controls">
              <button className="btn-small" onClick={() => setFocusPoint(null)}>
                Reset View
              </button>
            </div>
          </div>
          <EnhancedGlobe
            events={events}
            onEventClick={handleEventClick}
            focusPoint={focusPoint || undefined}
          />
        </div>

        <div className="panel source-panel">
          <div className="panel-header">
            <h2>SOURCES</h2>
          </div>
          <SourcePanel stats={sourceStats} />
        </div>

        <div className="panel threat-panel">
          <div className="panel-header">
            <h2>THREAT ASSESSMENT</h2>
          </div>
          <ThreatBar level={threatLevel} />
        </div>
      </div>

      <EventDetailModal event={selectedEvent} onClose={handleCloseModal} />
    </div>
  );
};
```

---

## File: src/App.tsx

```typescript
import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Dashboard } from './components/Dashboard';
import { EnhancedTerminal } from './components/EnhancedTerminal';
import { useWebSocket } from './hooks/useWebSocket';
import { useStore } from './store/useStore';
import './App.css';

const Navigation: React.FC = () => (
  <nav className="navigation">
    <div className="nav-brand">
      <h2>OSIN</h2>
      <span className="status-dot live"></span>
    </div>
    <div className="nav-links">
      <a href="/" className="nav-link">
        Dashboard
      </a>
      <a href="/terminal" className="nav-link">
        Terminal
      </a>
      <a href="/analytics" className="nav-link">
        Analytics
      </a>
    </div>
    <div className="nav-time">{new Date().toLocaleTimeString()}</div>
  </nav>
);

const App: React.FC = () => {
  useWebSocket();
  const { updateSourceStats, updateThreatLevel } = useStore();

  useEffect(() => {
    const interval = setInterval(() => {
      updateSourceStats({
        twitter: Math.floor(Math.random() * 20),
        reddit: Math.floor(Math.random() * 15),
        youtube: Math.floor(Math.random() * 10),
        news: Math.floor(Math.random() * 25),
        total: Math.floor(Math.random() * 70)
      });

      updateThreatLevel(Math.floor(Math.random() * 100));
    }, 5000);

    return () => clearInterval(interval);
  }, [updateSourceStats, updateThreatLevel]);

  return (
    <Router>
      <div className="app-container">
        <Navigation />
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/terminal" element={<EnhancedTerminal />} />
          <Route path="/analytics" element={<div className="page-content">Analytics Dashboard</div>} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
```
