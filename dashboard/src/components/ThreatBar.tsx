import React from 'react';
import { useStore } from '../store/useStore';
import '../styles/ThreatBar.css';

export const ThreatBar: React.FC = () => {
  const threatLevel = useStore((state) => state.threatLevel);

  const getThreatColor = (level: number) => {
    if (level < 25) return '#00ff00'; // Green
    if (level < 50) return '#ffff00'; // Yellow
    if (level < 75) return '#ff6600'; // Orange
    return '#ff0000'; // Red
  };

  const getThreatStatus = (level: number) => {
    if (level < 25) return 'GREEN';
    if (level < 50) return 'YELLOW';
    if (level < 75) return 'ORANGE';
    return 'RED';
  };

  return (
    <div className="threat-bar-container">
      <div className="threat-header">
        <h3>[THREAT LEVEL]</h3>
        <span className={`threat-status status-${getThreatStatus(threatLevel).toLowerCase()}`}>
          {getThreatStatus(threatLevel)}
        </span>
      </div>

      <div className="threat-bar">
        <div
          className="threat-fill"
          style={{
            width: `${threatLevel}%`,
            backgroundColor: getThreatColor(threatLevel),
          }}
        ></div>
      </div>

      <div className="threat-info">
        <span className="threat-percentage">{threatLevel.toFixed(1)}%</span>
        <span className="threat-description">
          {threatLevel < 25 && 'System Status: Normal'}
          {threatLevel >= 25 && threatLevel < 50 && 'System Status: Elevated'}
          {threatLevel >= 50 && threatLevel < 75 && 'System Status: High Alert'}
          {threatLevel >= 75 && 'System Status: Critical'}
        </span>
      </div>
    </div>
  );
};
