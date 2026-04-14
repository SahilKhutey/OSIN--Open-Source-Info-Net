export type OperationalMode = 
  | 'COMMAND_CENTER'
  | 'SATELLITE_OPS'
  | 'GEO_INTELLIGENCE'
  | 'TIME_TRAVEL'
  | 'AUTONOMOUS_CORE';

export type ConsciousnessStatus = 'ACTIVE' | 'STANDBY' | 'OFFLINE' | 'DEGRADED';
export type CoreStatus = 'OPERATIONAL' | 'LOADING' | 'OFFLINE' | 'SYNCING';
export type SafetyStatus = 'ENGAGED' | 'DISENGAGED' | 'OVERRIDE' | 'CRITICAL';
export type AutonomousMode = 'GOD_MODE' | 'ASSISTED' | 'MANUAL';

export interface SystemStatus {
  consciousness: ConsciousnessStatus;
  strategicCore: CoreStatus;
  graphDatabase: CoreStatus;
  safetyMonitor: SafetyStatus;
  autonomousMode: AutonomousMode;
  version: string;
}

export interface ConsciousnessState {
  confidence: number;
  uncertainty: number;
  strategicFocus: number;
  cognitiveLoad: number;
  missionProgress: number;
}

export interface TerminalLog {
  timestamp: string;
  message: string;
  type: 'info' | 'warn' | 'error' | 'success' | 'system';
}
