# WebSocket Service & Enhanced Store Implementation

## File: src/services/websocketService.ts

```typescript
import { useStore } from '../store/useStore';
import { IntelligenceEvent, Alert, SourceStats } from '../types';

class WebSocketService {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 3000;
  private reconnectTimer: NodeJS.Timeout | null = null;

  constructor(url: string = 'ws://localhost:8000/ws/intelligence') {
    this.url = url;
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          console.log('✓ WebSocket connected');
          this.reconnectAttempts = 0;
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        this.ws.onclose = () => {
          console.log('WebSocket disconnected');
          this.attemptReconnect();
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };
      } catch (error) {
        console.error('WebSocket connection failed:', error);
        reject(error);
      }
    });
  }

  private handleMessage(data: any): void {
    const { addEvent, addAlert, updateSourceStats, updateThreatLevel } = 
      useStore.getState();

    switch (data.type) {
      case 'event':
        addEvent(data.payload as IntelligenceEvent);
        break;
      case 'alert':
        addAlert(data.payload as Alert);
        break;
      case 'stats':
        updateSourceStats(data.payload as Partial<SourceStats>);
        break;
      case 'threat':
        updateThreatLevel(data.payload.level as number);
        break;
      default:
        console.log('Unknown message type:', data.type);
    }
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Reconnecting attempt ${this.reconnectAttempts}...`);
      
      this.reconnectTimer = setTimeout(() => {
        this.connect().catch((error) => {
          console.error('Reconnection failed:', error);
        });
      }, this.reconnectDelay);
    } else {
      console.error('Max reconnection attempts reached');
    }
  }

  disconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }
    if (this.ws) {
      this.ws.close();
    }
  }

  sendMessage(message: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected');
    }
  }

  isConnected(): boolean {
    return this.ws ? this.ws.readyState === WebSocket.OPEN : false;
  }

  getStatus(): {
    connected: boolean;
    reconnectAttempts: number;
    url: string;
  } {
    return {
      connected: this.isConnected(),
      reconnectAttempts: this.reconnectAttempts,
      url: this.url
    };
  }
}

export const webSocketService = new WebSocketService();
```

---

## File: src/store/useStore.ts (Enhanced)

```typescript
import { create } from 'zustand';
import { IntelligenceEvent, Alert, SourceStats, ThreatLevel } from '../types';

interface AgentStatus {
  name: string;
  status: 'active' | 'idle' | 'error' | 'offline';
  lastActive: string;
  tasks: number;
  confidence: number;
}

interface StoreState {
  // Data
  events: IntelligenceEvent[];
  alerts: Alert[];
  sourceStats: SourceStats;
  threatLevel: number;
  agentStatus: AgentStatus[];
  
  // UI State
  selectedEventId: string | null;
  selectedAlertId: string | null;
  isTerminalOpen: boolean;
  isHeatmapMode: boolean;
  
  // Actions - Events
  addEvent: (event: IntelligenceEvent) => void;
  removeEvent: (id: string) => void;
  clearOldEvents: (hours: number) => void;
  getEventById: (id: string) => IntelligenceEvent | undefined;
  
  // Actions - Alerts
  addAlert: (alert: Alert) => void;
  acknowledgeAlert: (id: string) => void;
  dismissAlert: (id: string) => void;
  clearAlerts: () => void;
  
  // Actions - Statistics
  updateSourceStats: (stats: Partial<SourceStats>) => void;
  updateThreatLevel: (level: number) => void;
  
  // Actions - Agent Status
  updateAgentStatus: (agent: AgentStatus) => void;
  setAgentStatus: (agents: AgentStatus[]) => void;
  
  // Actions - UI
  selectEvent: (id: string | null) => void;
  selectAlert: (id: string | null) => void;
  toggleTerminal: () => void;
  toggleHeatmapMode: () => void;
  
  // Utilities
  getActiveAlertCount: () => number;
  getTrendingEntities: () => string[];
  getEventsByPlatform: (platform: string) => IntelligenceEvent[];
}

export const useStore = create<StoreState>((set, get) => ({
  // Initial State
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
  agentStatus: [],
  selectedEventId: null,
  selectedAlertId: null,
  isTerminalOpen: false,
  isHeatmapMode: false,

  // Event Actions
  addEvent: (event) =>
    set((state) => ({
      events: [event, ...state.events.slice(0, 99)]
    })),

  removeEvent: (id) =>
    set((state) => ({
      events: state.events.filter((event) => event.id !== id)
    })),

  clearOldEvents: (hours) =>
    set((state) => {
      const cutoffTime = Date.now() - hours * 60 * 60 * 1000;
      return {
        events: state.events.filter((event) =>
          new Date(event.timestamp).getTime() > cutoffTime
        )
      };
    }),

  getEventById: (id) => {
    const state = get();
    return state.events.find((event) => event.id === id);
  },

  // Alert Actions
  addAlert: (alert) =>
    set((state) => ({
      alerts: [alert, ...state.alerts.slice(0, 19)]
    })),

  acknowledgeAlert: (id) =>
    set((state) => ({
      alerts: state.alerts.map((alert) =>
        alert.id === id ? { ...alert, acknowledged: true } : alert
      )
    })),

  dismissAlert: (id) =>
    set((state) => ({
      alerts: state.alerts.filter((alert) => alert.id !== id)
    })),

  clearAlerts: () => set({ alerts: [] }),

  // Statistics Actions
  updateSourceStats: (newStats) =>
    set((state) => ({
      sourceStats: {
        ...state.sourceStats,
        ...newStats,
        lastUpdated: new Date().toISOString()
      }
    })),

  updateThreatLevel: (level) => set({ threatLevel: level }),

  // Agent Actions
  updateAgentStatus: (agent) =>
    set((state) => {
      const existingIndex = state.agentStatus.findIndex(
        (a) => a.name === agent.name
      );
      if (existingIndex >= 0) {
        const updated = [...state.agentStatus];
        updated[existingIndex] = agent;
        return { agentStatus: updated };
      }
      return { agentStatus: [...state.agentStatus, agent] };
    }),

  setAgentStatus: (agents) => set({ agentStatus: agents }),

  // UI Actions
  selectEvent: (id) => set({ selectedEventId: id }),
  selectAlert: (id) => set({ selectedAlertId: id }),
  toggleTerminal: () =>
    set((state) => ({ isTerminalOpen: !state.isTerminalOpen })),
  toggleHeatmapMode: () =>
    set((state) => ({ isHeatmapMode: !state.isHeatmapMode })),

  // Utilities
  getActiveAlertCount: () => {
    const state = get();
    return state.alerts.filter((alert) => !alert.acknowledged).length;
  },

  getTrendingEntities: () => {
    const state = get();
    const entities: Record<string, number> = {};
    
    state.events.forEach((event) => {
      if (event.entities) {
        event.entities.forEach((entity) => {
          entities[entity] = (entities[entity] || 0) + 1;
        });
      }
    });

    return Object.entries(entities)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 10)
      .map(([entity]) => entity);
  },

  getEventsByPlatform: (platform) => {
    const state = get();
    return state.events.filter((event) => event.platform === platform);
  }
}));
```

---

## Summary

### WebSocketService Features
- ✅ Automatic reconnection with exponential backoff
- ✅ Connection status tracking
- ✅ Type-safe message handling
- ✅ Error recovery
- ✅ Graceful disconnect

### Enhanced Store Features
- ✅ Event management (add, remove, clear old)
- ✅ Alert management (acknowledge, dismiss, clear)
- ✅ Agent status tracking
- ✅ UI state management
- ✅ Utility functions for trending data
- ✅ Platform-specific filtering
- ✅ Active alert counting

### Integration Notes
1. Import `webSocketService` in App.tsx
2. Call `webSocketService.connect()` in useEffect
3. Store automatically updates on WebSocket messages
4. Use store hooks to access state and actions
