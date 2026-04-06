export type ThreatLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type Severity = 'low' | 'medium' | 'high' | 'critical';

export interface Location {
  lat: number;
  lng: number;
  country?: string;
  city?: string;
}

export interface IntelligenceEvent {
  id: string;
  timestamp: number;
  source: string;
  type: string;
  severity: Severity;
  content: string;
  platform?: string;
  confidence?: number;
  location?: Location;
  data?: Record<string, unknown>;
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
