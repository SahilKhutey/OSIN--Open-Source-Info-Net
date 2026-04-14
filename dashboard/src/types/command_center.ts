export interface Alert {
  id: string;
  level: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  message: string;
  msg?: string; // Compatibility
  location?: { lat: number; lon: number };
  lat: number;
  lon: number;
  timestamp: Date;
  source: string;
  confidence: number;
  type: string;
  timeIndex?: number;
}

export interface GraphConnection {
  id: string;
  from: string;
  to: string;
  strength: number;
  type: string;
  timeIndex?: number;
}

export interface ChatMessage {
  role: 'user' | 'ai' | 'agent' | 'system';
  text: string;
  timestamp: Date;
}

export type TimeIndex = 1 | 2 | 3 | 4 | 5;

export interface LLMResponse {
  response: string;
  confidence: number;
  recommendations: string[];
}

export interface SystemStatus {
  ingestion?: 'ACTIVE' | 'DEGRADED' | 'OFFLINE';
  graphCore?: 'ONLINE' | 'SYNCING' | 'OFFLINE';
  aiReasoning?: 'STABLE' | 'LOADING' | 'OFFLINE' | 'ANALYZING';
  threatLevel?: 'CRITICAL' | 'HIGH' | 'ELEVATED' | 'NORMAL';
  globalRisk?: number;
  voiceAnalyst?: 'ONLINE' | 'SPEAKING' | 'OFFLINE';
  simulation?: 'READY' | 'RUNNING' | 'COMPLETE';
  aiCommand?: 'ONLINE' | 'PROCESSING';
  timeTravel?: 'ACTIVE' | 'PAUSED';
  // New Autonomous Statuses
  llmBackend?: 'CONNECTED' | 'PROCESSING' | 'DISCONNECTED';
  satelliteLayer?: 'ACTIVE' | 'STANDBY' | 'OFFLINE';
  graphDatabase?: 'ACTIVE' | 'SYNCING' | 'OFFLINE';
  autonomousMode?: 'ACTIVE' | 'STANDBY' | 'OFFLINE';
  propagationEngine?: 'READY' | 'RUNNING' | 'COMPLETE';
}

export interface GlobeProps {
  alerts: Alert[];
  onAlertSelect: (alert: Alert) => void;
  onGlobeClick: (lat: number, lon: number) => void;
  className?: string;
  connections?: GraphConnection[];
}
