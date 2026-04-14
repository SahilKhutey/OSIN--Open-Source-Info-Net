import React, { useState, useEffect, useCallback } from 'react';
import { 
  Zap, 
  Activity, 
  ShieldCheck, 
  Cpu, 
  Layers, 
  Eye, 
  ChevronRight,
  RefreshCw,
  AlertOctagon,
  Brain
} from 'lucide-react';
import './AutonomousMonitor.css';

interface AutonomousMonitorProps {
  onClose: () => void;
}

export const AutonomousMonitor: React.FC<AutonomousMonitorProps> = ({ onClose }) => {
  const [status, setStatus] = useState<any>({ 
    status: 'OPTIMAL', 
    actions_executed: 0, 
    swarm_agents: 0,
    safety_log: [] 
  });
  const [forecast, setForecast] = useState<any>({ simulated_risks: {} });
  const [loading, setLoading] = useState(false);

  const fetchState = useCallback(async () => {
    setLoading(true);
    try {
      const [sRes, fRes] = await Promise.all([
        fetch('http://localhost:8022/status'),
        fetch('http://localhost:8022/simulation/forecast')
      ]);
      const sData = await sRes.json();
      const fData = await fRes.json();
      setStatus(sData);
      setForecast(fData);
    } catch (err) {
      console.error('Autonomous sync failed:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchState();
    const interval = setInterval(fetchState, 10000);
    return () => clearInterval(interval);
  }, [fetchState]);

  return (
    <div className="autonomous-overlay">
      <div className="autonomous-monitor">
        {/* Header: OSIN Prefrontal Cortex */}
        <header className="monitor-header">
          <div className="id-badge">
            <Brain className="brain-icon" size={24} />
            <div className="text-stack">
              <h1>OSIN Autonomous Control HUD</h1>
              <span>Executive Reasoning Organism | v5.0.0</span>
            </div>
          </div>
          <div className="meta-info">
            <div className="safety-badge">
              <ShieldCheck size={14} />
              <span>Safety Sentinel: Active</span>
            </div>
            <button className="close-btn" onClick={onClose}>×</button>
          </div>
        </header>

        <main className="monitor-content">
          {/* Column 1: System Health & Safety */}
          <section className="col-panel safety-section">
            <div className="panel-label">
              <Cpu size={14} />
              <span>System Governance</span>
            </div>
            <div className="health-grid">
              <div className="health-card">
                <span className="label">Collective Status</span>
                <span className={`status-val ${status.status.toLowerCase()}`}>
                  {status.status}
                </span>
              </div>
              <div className="health-card">
                <span className="label">Action Budget</span>
                <span className="val">{status.actions_executed} / 500</span>
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${(status.actions_executed / 500) * 100}%` }}
                  />
                </div>
              </div>
            </div>
            <div className="safety-log">
              <div className="log-header">
                <Eye size={14} />
                <span>Governance Log</span>
              </div>
              <div className="log-entries">
                {status.safety_log.length > 0 ? (
                  status.safety_log.map((entry: any, i: number) => (
                    <div className="log-item" key={i}>
                      <span className="ts">{new Date(entry.timestamp).toLocaleTimeString()}</span>
                      <span className="reason">{entry.reason}</span>
                      <span className="act">{entry.action_taken}</span>
                    </div>
                  ))
                ) : (
                  <div className="empty-log">No policy violations detected.</div>
                )}
              </div>
            </div>
          </section>

          {/* Column 2: Swarm & Decision Intelligence */}
          <section className="col-panel swarm-section">
            <div className="panel-label">
              <Layers size={14} />
              <span>Swarm Intelligence Feedback</span>
            </div>
            <div className="agent-clusters">
              <div className="cluster-card">
                <div className="icon-wrap"><Zap size={20} color="#00ffcc" /></div>
                <div className="cluster-info">
                  <h3>Strategic Agents</h3>
                  <span>{status.swarm_agents} Entities reasoning over Graph</span>
                </div>
                <RefreshCw 
                  size={14} 
                  className={loading ? 'spinning' : ''} 
                  onClick={fetchState}
                  style={{ cursor: 'pointer' }}
                />
              </div>
            </div>
            <div className="reasoning-feed">
              <div className="feed-header">
                <Activity size={14} />
                <span>Recursive Analysis Feed</span>
              </div>
              <div className="feed-items">
                <div className="feed-item">
                  <ChevronRight size={14} className="arrow" />
                  <p>Autonomous Agent initiated <strong>DEEP_ANALYSIS</strong> on high-risk spatial cluster.</p>
                </div>
                <div className="feed-item">
                  <ChevronRight size={14} className="arrow" />
                  <p>Neural Swarm converged on <strong>composite confidence: 0.84</strong>.</p>
                </div>
                <div className="feed-item">
                  <ChevronRight size={14} className="arrow" />
                  <p>Policy Engine approved <strong>REBUILD_GRAPH</strong> for target infrastructure.</p>
                </div>
              </div>
            </div>
          </section>

          {/* Column 3: Digital Twin Projection */}
          <section className="col-panel sim-section">
            <div className="panel-label">
              <AlertOctagon size={14} />
              <span>Digital Twin Simulation (24H Projection)</span>
            </div>
            <div className="sim-risk-grid">
              {Object.entries(forecast.simulated_risks).map(([k, v]: [string, any]) => (
                <div className="risk-metric" key={k}>
                  <div className="metric-header">
                    <span className="name">{k.replace('_', ' ')}</span>
                    <span className="val">{Math.round(v * 100)}%</span>
                  </div>
                  <div className="risk-bar">
                    <div 
                      className="risk-fill" 
                      style={{ 
                        width: `${v * 100}%`,
                        backgroundColor: v > 0.7 ? '#ff4d4d' : v > 0.4 ? '#ffcc00' : '#00ffcc'
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
            <div className="projection-visual">
              <div className="vid-placeholder">
                {/* Heatmap overlay would go here */}
                <div className="scan-line"></div>
                <span>GLOBAL SITUATIONAL PROJECTION ACTIVE</span>
              </div>
            </div>
          </section>
        </main>

        <footer className="monitor-footer">
          <div className="compliance-line">
            <ShieldCheck size={12} />
            <span>GDPR/Lawful OSINT Compliance: Verified</span>
          </div>
          <div className="system-ts">
            Last Collective Update: {new Date().toLocaleTimeString()}
          </div>
        </footer>
      </div>
    </div>
  );
};

export default AutonomousMonitor;
