import React, { useState, useEffect, useCallback } from 'react';
import { 
  Activity, 
  AlertTriangle, 
  Brain, 
  TrendingUp, 
  Zap, 
  Shield, 
  Target,
  Clock,
  ChevronRight
} from 'lucide-react';
import './LiveOSINDashboard.css';

interface LiveOSINDashboardProps {
  onClose: () => void;
}

export const LiveOSINDashboard: React.FC<LiveOSINDashboardProps> = ({ onClose }) => {
  const [status, setStatus] = useState<any>({ entities: 0, status: 'BOOTING' });
  const [threat, setThreat] = useState<any>({ prediction: 0, threat_level: 'LOW' });
  const [liveLog, setLiveLog] = useState<any[]>([]);

  const fetchData = useCallback(async () => {
    try {
      const [sRes, tRes] = await Promise.all([
        fetch('http://localhost:8021/status'),
        fetch('http://localhost:8021/threat-prediction')
      ]);
      const sData = await sRes.json();
      const tData = await tRes.json();
      setStatus(sData);
      setThreat(tData);
    } catch (err) {
      console.error('Real-time poll failed:', err);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, [fetchData]);

  // Mock live log for effect (would be WebSocket in prod)
  useEffect(() => {
    const types = ['GEO_INTEL', 'CYBER_INTEL', 'SIGNAL_INTEL', 'THREAT_SYNC'];
    const interval = setInterval(() => {
      const newEntry = {
        id: Math.random().toString(36).substr(2, 9),
        type: types[Math.floor(Math.random() * types.length)],
        time: new Date().toLocaleTimeString(),
        status: Math.random() > 0.3 ? 'PROCESSED' : 'REASONING'
      };
      setLiveLog(prev => [newEntry, ...prev.slice(0, 14)]);
    }, 1500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="live-osin-overlay">
      <div className="live-osin-dashboard">
        {/* Header Section */}
        <header className="live-header">
          <div className="system-branding">
            <Zap className="accent-icon" size={24} />
            <div className="brand-stack">
              <h1>OSIN Live Intelligence Observatory</h1>
              <span>Unified Real-Time Situational Awareness | v4.0.0</span>
            </div>
          </div>
          <div className="system-status">
            <div className="status-item">
              <span className="label">Engines:</span>
              <span className="val active">Online</span>
            </div>
            <div className="status-item">
              <span className="label">Latency:</span>
              <span className="val">14ms</span>
            </div>
            <button className="close-panel" onClick={onClose}>×</button>
          </div>
        </header>

        <main className="live-content">
          {/* Column 1: Threat Forecasting */}
          <section className="live-panel threat-panel">
            <div className="panel-header">
              <Shield size={18} />
              <h2>Threat Prediction Engine</h2>
            </div>
            <div className="prediction-display">
              <div className="meter-container">
                <div 
                  className={`intensity-ring ${threat.threat_level.toLowerCase()}`}
                  style={{ '--intensity': `${threat.prediction * 100}%` } as any}
                >
                  <span className="percent">{Math.round(threat.prediction * 100)}%</span>
                  <span className="label">Intensity</span>
                </div>
              </div>
              <div className="prediction-meta">
                <div className="meta-row">
                  <span className="key">Forecast Level:</span>
                  <span className={`val highlight ${threat.threat_level.toLowerCase()}`}>
                    {threat.threat_level}
                  </span>
                </div>
                <div className="meta-row">
                  <span className="key">Model Confidence:</span>
                  <span className="val">92.4%</span>
                </div>
              </div>
            </div>
            <div className="prediction-trend">
              <TrendingUp size={14} />
              <span>Trend: Stable (Random Forest v4.1)</span>
            </div>
          </section>

          {/* Column 2: Event Stream Log */}
          <section className="live-panel log-panel">
            <div className="panel-header">
              <Activity size={18} />
              <h2>Live Intelligence Bus</h2>
            </div>
            <div className="log-container">
              {liveLog.map(entry => (
                <div key={entry.id} className="log-entry">
                  <span className="time">{entry.time}</span>
                  <span className="type">{entry.type}</span>
                  <div className={`status ${entry.status.toLowerCase()}`}>
                    <div className="dot"></div>
                    {entry.status}
                  </div>
                  <ChevronRight size={14} className="arrow" />
                </div>
              ))}
            </div>
          </section>

          {/* Column 3: AI Reasoning & Metrics */}
          <section className="live-panel ai-panel">
            <div className="panel-header">
              <Brain size={18} />
              <h2>Reasoning Core</h2>
            </div>
            <div className="insight-card">
              <div className="card-header">
                <Target size={14} />
                <span>Active Situational Insight</span>
              </div>
              <p>
                "Autonomous reasoning in progress. Detected <strong>{status.entities}</strong> distinct 
                intelligence entities. Cross-layer graph linking has identified a pattern in 
                Cyber-Physical signals. <strong>Recommendation:</strong> Deep scan target infrastructure 
                for infrastructure leaks."
              </p>
            </div>
            <div className="graph-metrics">
              <div className="metric-box">
                <span className="val">{status.entities}</span>
                <span className="label">Graph Entities</span>
              </div>
              <div className="metric-box">
                <span className="val">{Math.round(status.entities * 1.4)}</span>
                <span className="label">Total Links</span>
              </div>
            </div>
          </section>
        </main>

        <footer className="live-footer">
          <div className="node-info">
            <Clock size={12} />
            <span>Master Orchestrator: Running on Port 8021</span>
          </div>
          <div className="security-seal">
            <Shield size={12} />
            <span>Encrypted Stream | OSIN-KAFKA-V4</span>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default LiveOSINDashboard;
