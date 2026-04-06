# React TypeScript Dashboard

A modern, real-time dashboard built with React, TypeScript, Vite, Three.js, and WebSocket support.

## Project Structure

```
dashboard/
├── src/
│   ├── components/          # React components
│   ├── hooks/               # Custom React hooks
│   │   └── useWebSocket.ts  # WebSocket integration hook
│   ├── store/               # Zustand state management
│   │   └── useStore.ts      # Main store with actions
│   ├── types/               # TypeScript type definitions
│   │   └── index.ts         # All shared types and interfaces
│   └── services/            # External services
│       └── websocketService.ts  # WebSocket service class
├── public/                  # Static assets
├── package.json             # Dependencies and scripts
├── tsconfig.json            # TypeScript configuration
├── tsconfig.node.json       # TypeScript config for Vite
├── vite.config.ts           # Vite configuration
└── README.md               # This file
```

## Features

- **React 18** with TypeScript for type-safe development
- **Vite** for fast development and optimized builds
- **Zustand** for lightweight state management
- **WebSocket** real-time data streaming with auto-reconnect
- **Three.js** and **react-globe.gl** for 3D visualization
- **Axios** for HTTP requests
- **Strict TypeScript** configuration for code quality

## Installation

```bash
npm install
```

## Development

Start the development server:

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## Build

Create an optimized production build:

```bash
npm run build
```

## Type Definitions

All TypeScript interfaces are defined in `src/types/index.ts`:

- **ThreatLevel**: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
- **AgentStatus**: 'ACTIVE' | 'INACTIVE' | 'MONITORING'
- **IntelligenceEvent**: Represents intelligence data events
- **Alert**: System alerts with severity levels
- **SourceStats**: Statistics for data sources
- **DashboardState**: Main application state interface

## State Management

The store (`src/store/useStore.ts`) manages:

- Events list (capped at 100 items)
- Alerts list (capped at 50 items)
- Source statistics
- Current threat level
- WebSocket connection status
- Error messages

Actions available:
- `addEvent()` - Add new event
- `addAlert()` - Add new alert
- `updateSourceStats()` - Update source statistics
- `setThreatLevel()` - Update threat level
- `setConnected()` - Update connection status
- `setError()` - Set error message
- `clearEvents()` - Clear events list
- `clearAlerts()` - Clear alerts list

## WebSocket Integration

### Using the Hook

```typescript
import { useWebSocket } from '@/hooks';

function MyComponent() {
  const { send, disconnect } = useWebSocket('ws://localhost:8000');
  
  // Component logic here
}
```

### WebSocket Service

The `WebSocketService` class provides:

- Auto-reconnecting WebSocket connection
- Message parsing and distribution
- Listener subscription system
- Automatic store integration

## Dependencies

- **react**: UI framework
- **react-dom**: React DOM rendering
- **vite**: Build tool and dev server
- **typescript**: Type checking
- **zustand**: State management
- **three**: 3D graphics
- **react-globe.gl**: Globe visualization
- **reconnecting-websocket**: Resilient WebSocket
- **axios**: HTTP client

## Development Scripts

- `npm run dev` - Start development server
- `npm run build` - Create production build
- `npm run preview` - Preview production build

## License

MIT
