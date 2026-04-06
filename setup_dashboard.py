#!/usr/bin/env python3
"""Setup dashboard directory structure and create project files."""

import os
import json
from pathlib import Path

# Define the base path
base_path = Path(r"C:\Users\User\Documents\OSIN\dashboard")

# Create directory structure
directories = [
    "src/components",
    "src/hooks",
    "src/store",
    "src/types",
    "src/services",
    "public"
]

print(f"Creating dashboard at: {base_path}")

# Create all directories
for directory in directories:
    dir_path = base_path / directory
    dir_path.mkdir(parents=True, exist_ok=True)
    print(f"✓ Created directory: {dir_path}")

# package.json
package_json = {
    "name": "dashboard",
    "private": True,
    "version": "0.0.1",
    "type": "module",
    "scripts": {
        "dev": "vite",
        "build": "tsc -b && vite build",
        "preview": "vite preview"
    },
    "dependencies": {
        "react": "^18.3.1",
        "react-dom": "^18.3.1",
        "three": "^r128",
        "react-globe.gl": "^2.29.0",
        "zustand": "^4.4.1",
        "reconnecting-websocket": "^4.4.0",
        "axios": "^1.6.2"
    },
    "devDependencies": {
        "@types/react": "^18.2.56",
        "@types/react-dom": "^18.2.19",
        "@vitejs/plugin-react": "^4.2.4",
        "typescript": "^5.3.3",
        "vite": "^5.0.10"
    }
}

with open(base_path / "package.json", "w") as f:
    json.dump(package_json, f, indent=2)
print("✓ Created package.json")

# tsconfig.json
tsconfig = {
    "compilerOptions": {
        "target": "ES2020",
        "useDefineForClassFields": True,
        "lib": ["ES2020", "DOM", "DOM.Iterable"],
        "module": "ESNext",
        "skipLibCheck": True,
        "esModuleInterop": True,
        "allowSyntheticDefaultImports": True,
        "moduleResolution": "bundler",
        "allowImportingTsExtensions": True,
        "resolveJsonModule": True,
        "isolatedModules": True,
        "noEmit": True,
        "jsx": "react-jsx",
        "strict": True,
        "noUnusedLocals": True,
        "noUnusedParameters": True,
        "noFallthroughCasesInSwitch": True,
        "baseUrl": ".",
        "paths": {
            "@/*": ["src/*"]
        }
    },
    "include": ["src"],
    "references": [{"path": "./tsconfig.node.json"}]
}

with open(base_path / "tsconfig.json", "w") as f:
    json.dump(tsconfig, f, indent=2)
print("✓ Created tsconfig.json")

# tsconfig.node.json
tsconfig_node = {
    "compilerOptions": {
        "composite": True,
        "skipLibCheck": True,
        "module": "ESNext",
        "moduleResolution": "bundler",
        "allowSyntheticDefaultImports": True
    },
    "include": ["vite.config.ts"]
}

with open(base_path / "tsconfig.node.json", "w") as f:
    json.dump(tsconfig_node, f, indent=2)
print("✓ Created tsconfig.node.json")

# vite.config.ts
vite_config = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true
  }
})
"""

with open(base_path / "vite.config.ts", "w") as f:
    f.write(vite_config)
print("✓ Created vite.config.ts")

# src/types/index.ts
types_file = '''export type ThreatLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export type AgentStatus = 'ACTIVE' | 'INACTIVE' | 'MONITORING';

export interface IntelligenceEvent {
  id: string;
  timestamp: number;
  source: string;
  type: string;
  severity: ThreatLevel;
  description: string;
  data: Record<string, unknown>;
}

export interface Alert {
  id: string;
  timestamp: number;
  type: string;
  severity: ThreatLevel;
  message: string;
  resolved: boolean;
}

export interface SourceStats {
  source: string;
  eventCount: number;
  alertCount: number;
  lastUpdate: number;
}

export interface DashboardState {
  events: IntelligenceEvent[];
  alerts: Alert[];
  sourceStats: SourceStats[];
  threatLevel: ThreatLevel;
  isConnected: boolean;
  error: string | null;
}
'''

with open(base_path / "src" / "types" / "index.ts", "w") as f:
    f.write(types_file)
print("✓ Created src/types/index.ts")

# src/store/useStore.ts
store_file = '''import { create } from 'zustand';
import { DashboardState, IntelligenceEvent, Alert, SourceStats, ThreatLevel } from '../types';

interface StoreActions {
  addEvent: (event: IntelligenceEvent) => void;
  addAlert: (alert: Alert) => void;
  updateSourceStats: (stats: SourceStats[]) => void;
  setThreatLevel: (level: ThreatLevel) => void;
  setConnected: (connected: boolean) => void;
  setError: (error: string | null) => void;
  clearEvents: () => void;
  clearAlerts: () => void;
}

export const useStore = create<DashboardState & StoreActions>((set) => ({
  events: [],
  alerts: [],
  sourceStats: [],
  threatLevel: 'LOW',
  isConnected: false,
  error: null,

  addEvent: (event) =>
    set((state) => ({
      events: [event, ...state.events].slice(0, 100),
    })),

  addAlert: (alert) =>
    set((state) => ({
      alerts: [alert, ...state.alerts].slice(0, 50),
    })),

  updateSourceStats: (stats) =>
    set({
      sourceStats: stats,
    }),

  setThreatLevel: (level) =>
    set({
      threatLevel: level,
    }),

  setConnected: (connected) =>
    set({
      isConnected: connected,
    }),

  setError: (error) =>
    set({
      error,
    }),

  clearEvents: () =>
    set({
      events: [],
    }),

  clearAlerts: () =>
    set({
      alerts: [],
    }),
}));
'''

with open(base_path / "src" / "store" / "useStore.ts", "w") as f:
    f.write(store_file)
print("✓ Created src/store/useStore.ts")

# src/services/websocketService.ts
ws_service = '''import ReconnectingWebSocket from 'reconnecting-websocket';
import { DashboardState, IntelligenceEvent, Alert, SourceStats } from '../types';

export class WebSocketService {
  private ws: ReconnectingWebSocket | null = null;
  private url: string;
  private listeners: Set<(data: Partial<DashboardState>) => void> = new Set();

  constructor(url: string) {
    this.url = url;
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new ReconnectingWebSocket(this.url);

        this.ws.onopen = () => {
          console.log('WebSocket connected');
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };

        this.ws.onclose = () => {
          console.log('WebSocket disconnected');
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  private handleMessage(message: any): void {
    const update: Partial<DashboardState> = {};

    if (message.type === 'event' && message.payload) {
      update.events = [message.payload];
    }

    if (message.type === 'alert' && message.payload) {
      update.alerts = [message.payload];
    }

    if (message.type === 'stats' && message.payload) {
      update.sourceStats = message.payload;
    }

    if (message.type === 'threat_level' && message.payload) {
      update.threatLevel = message.payload;
    }

    if (Object.keys(update).length > 0) {
      this.notifyListeners(update);
    }
  }

  subscribe(listener: (data: Partial<DashboardState>) => void): () => void {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  }

  private notifyListeners(update: Partial<DashboardState>): void {
    this.listeners.forEach((listener) => {
      listener(update);
    });
  }

  send(data: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}
'''

with open(base_path / "src" / "services" / "websocketService.ts", "w") as f:
    f.write(ws_service)
print("✓ Created src/services/websocketService.ts")

# src/hooks/useWebSocket.ts
hook_file = '''import { useEffect, useRef } from 'react';
import { WebSocketService } from '../services/websocketService';
import { useStore } from '../store/useStore';
import { DashboardState } from '../types';

export const useWebSocket = (url: string) => {
  const wsRef = useRef<WebSocketService | null>(null);
  const store = useStore();

  useEffect(() => {
    wsRef.current = new WebSocketService(url);

    wsRef.current.connect()
      .then(() => {
        store.setConnected(true);
        store.setError(null);
      })
      .catch((error) => {
        console.error('Failed to connect WebSocket:', error);
        store.setError(error.message);
        store.setConnected(false);
      });

    const unsubscribe = wsRef.current.subscribe((update: Partial<DashboardState>) => {
      if (update.events && update.events.length > 0) {
        update.events.forEach((event) => {
          store.addEvent(event);
        });
      }

      if (update.alerts && update.alerts.length > 0) {
        update.alerts.forEach((alert) => {
          store.addAlert(alert);
        });
      }

      if (update.sourceStats) {
        store.updateSourceStats(update.sourceStats);
      }

      if (update.threatLevel) {
        store.setThreatLevel(update.threatLevel);
      }
    });

    return () => {
      unsubscribe();
      if (wsRef.current) {
        wsRef.current.disconnect();
      }
    };
  }, [url, store]);

  return {
    send: (data: any) => wsRef.current?.send(data),
    disconnect: () => wsRef.current?.disconnect(),
  };
};
'''

with open(base_path / "src" / "hooks" / "useWebSocket.ts", "w") as f:
    f.write(hook_file)
print("✓ Created src/hooks/useWebSocket.ts")

# Create .gitignore
gitignore = """# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

node_modules
dist
dist-ssr
*.local

# Editor directories and files
.vscode/*
!.vscode/extensions.json
.idea
.DS_Store
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?

# Environment variables
.env
.env.local
.env.*.local
"""

with open(base_path / ".gitignore", "w") as f:
    f.write(gitignore)
print("✓ Created .gitignore")

print("\n✓ Dashboard directory structure and all files created successfully!")
