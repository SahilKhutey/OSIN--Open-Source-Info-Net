import React, { useState, useEffect, useRef } from 'react';
import './GeoPrecisionPanel.css';

interface GeoPrecisionPanelProps {
  onWaypointsAnalyzed: (result: any) => void;
  onClose: () => void;
}

export const GeoPrecisionPanel: React.FC<GeoPrecisionPanelProps> = ({ 
  onWaypointsAnalyzed, 
  onClose 
}) => {
  const [activeTab, setActiveTab] = useState('waypoints');
  const [rtkStatus, setRtkStatus] = useState('disconnected');
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // Simulated RTK Stream Connection
    const ws = new WebSocket('ws://localhost:8013/ws/rtk-stream');
    ws.onopen = () => setRtkStatus('connected');
    ws.onclose = () => setRtkStatus('disconnected');
    ws.onerror = () => setRtkStatus('error');
    return () => ws.close();
  }, []);

  const handleWaypoints = async (file: File) => {
    const reader = new FileReader();
    reader.onload = async (e) => {
      try {
        const waypoints = JSON.parse(e.target?.result as string);
        const response = await fetch('http://localhost:8013/analyze-waypoints', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ waypoints, analysis_type: 'advanced' })
        });
        const result = await response.json();
        setAnalysisResult(result);
        onWaypointsAnalyzed(result);
      } catch (err) {
        console.error('Precision audit failed:', err);
      }
    };
    reader.readAsText(file);
  };

  return (
    <div className="precision-overlay">
      <div className="precision-container">
        <div className="precision-header">
          <div className="title-stack">
            <h3>🛰️ Geo Precision Intel</h3>
            <span>PNT Strategic Core | v3.1.0</span>
          </div>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="precision-tabs">
          {['waypoints', 'rtk', 'simulation', 'atlas'].map(tab => (
            <button 
              key={tab}
              className={activeTab === tab ? 'active' : ''}
              onClick={() => setActiveTab(tab)}
            >
              {tab}
            </button>
          ))}
        </div>

        <div className="precision-body">
          {activeTab === 'waypoints' && (
            <div className="tab-pane">
              <div className="drop-zone-precision" onClick={() => fileInputRef.current?.click()}>
                <div className="icon">📍</div>
                <p>Upload GNSS Waypoints (JSON)</p>
                <span>RTK Patterns & Speed Auditing</span>
              </div>
              <input 
                type="file" 
                ref={fileInputRef} 
                style={{ display: 'none' }} 
                onChange={e => e.target.files?.[0] && handleWaypoints(e.target.files[0])}
              />
              {analysisResult && (
                <div className="stats-grid">
                  <div className="stat">
                    <label>Total Dist</label>
                    <div>{analysisResult.results.total_distance_km.toFixed(2)} km</div>
                  </div>
                  <div className="stat">
                    <label>Max Speed</label>
                    <div>{analysisResult.results.max_speed_kmh.toFixed(1)} km/h</div>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'rtk' && (
            <div className="tab-pane">
              <div className={`status-hud ${rtkStatus}`}>
                <div className="pulse" />
                RTK Status: {rtkStatus.toUpperCase()}
              </div>
              <div className="station-list">
                <div className="station online">📡 rtk2go.com:2101 [MPC]</div>
                <div className="station offline">📡 local-base:2101 [BASE]</div>
              </div>
            </div>
          )}
        </div>

        <div className="precision-footer">
          RTKLIB 2.4.3 | kinematic | L1+L2+L5
        </div>
      </div>
    </div>
  );
};

export default GeoPrecisionPanel;
