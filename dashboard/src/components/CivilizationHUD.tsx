import React, { useState, useEffect, useCallback } from 'react';
import { 
  Globe, 
  Users, 
  Share2, 
  ShieldAlert, 
  Zap,
  TrendingUp,
  Cpu,
  RefreshCw,
  Search,
  ChevronRight
} from 'lucide-react';
import './CivilizationHUD.css';

interface CivilizationHUDProps {
  onClose: () => void;
}

export const CivilizationHUD: React.FC<CivilizationHUDProps> = ({ onClose }) => {
  const [data, setData] = useState<any>({ 
    status: 'ASCENDING', 
    civilization: { population_size: 0, stability: 0, network_density: 0 },
    swarm: { total_replicated: 0, recent_replications: [], capabilities: [] },
    forecast: { predicted_risk: 0, threat_level: 'STABLE', confidence: 0 }
  });

  const fetchData = useCallback(async () => {
    try {
      const res = await fetch('http://localhost:8024/status');
      const sData = await res.json();
      setData(sData);
    } catch (err) {
      console.error('Civilization sync failed:', err);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const riskColor = data.forecast.predicted_risk > 0.7 ? '#ff4757' : 
                   data.forecast.predicted_risk > 0.4 ? '#ffa502' : '#2ed573';

  return (
    <div className="civ-overlay">
      <div className="civ-hud">
        {/* Header: OSIN Ascension */}
        <header className="hud-header">
          <div className="hud-branding">
            <Globe className="icon-glow" size={24} />
            <div className="title-stack">
              <h1>Digital Nation Simulation</h1>
              <span>Synthetic Intelligence Civilization | v7.0.0 Ascension</span>
            </div>
          </div>
          <div className="hud-meta">
            <div className="status-badge pulse-border">
              <Zap size={14} />
              <span>{data.status}</span>
            </div>
            <button className="close-btn" onClick={onClose}>×</button>
          </div>
        </header>

        <main className="hud-content">
          {/* Column 1: Society Dynamics */}
          <section className="hud-panel society-panel">
            <div className="panel-label">
              <Users size={14} />
              <span>Society Dynamics</span>
            </div>
            <div className="civ-stats-grid">
              <div className="civ-stat">
                <span className="label">Population Size</span>
                <span className="val">{data.civilization.population_size}</span>
                <div className="sub">Entities Active</div>
              </div>
              <div className="civ-stat">
                <span className="label">Network Density</span>
                <span className="val">{(data.civilization.network_density * 100).toFixed(2)}%</span>
                <div className="sub">Social Fabric</div>
              </div>
            </div>
            <div className="stability-meter">
              <div className="meter-label">
                <span>Civilization Stability</span>
                <span>{Math.round(data.civilization.stability * 100)}%</span>
              </div>
              <div className="meter-track">
                <div className="meter-fill" style={{ 
                  width: `${data.civilization.stability * 100}%`,
                  background: data.civilization.stability > 0.7 ? '#2ed573' : '#ffa502'
                }} />
              </div>
            </div>
          </section>

          {/* Column 2: Swarm Replication */}
          <section className="hud-panel swarm-panel">
            <div className="panel-label">
              <Cpu size={14} />
              <span>Autonomous Swarm Replication</span>
            </div>
            <div className="swarm-hero">
              <div className="hero-val">{data.swarm.total_replicated}</div>
              <div className="hero-label">Replicated Agents</div>
            </div>
            <div className="capability-cloud">
              {data.swarm.capabilities.map((cap: string) => (
                <div className="cap-tag" key={cap}>
                  <RefreshCw size={10} />
                  <span>{cap.replace('_', ' ')}</span>
                </div>
              ))}
            </div>
            <div className="recent-logs">
              <div className="log-header">Recent Genome Events</div>
              {data.swarm.recent_replications.map((rep: any) => (
                <div className="log-entry" key={rep.id}>
                  <ChevronRight size={10} color="#00ffcc" />
                  <span className="rep-id">{rep.id}</span>
                  <span className="rep-cap">{rep.capability}</span>
                </div>
              ))}
            </div>
          </section>

          {/* Column 3: Global Forecasting */}
          <section className="hud-panel forecast-panel">
            <div className="panel-label">
              <ShieldAlert size={14} />
              <span>World-Scale Forecasting</span>
            </div>
            <div className="risk-forecast" style={{ borderColor: riskColor }}>
              <div className="risk-level" style={{ color: riskColor }}>
                {data.forecast.threat_level}
              </div>
              <div className="risk-sub">Global Threat Horizon</div>
              <div className="risk-score">{(data.forecast.predicted_risk * 100).toFixed(1)}%</div>
              <div className="risk-label">Risk Probability</div>
            </div>
            <div className="forecast-meta">
              <div className="meta-item">
                <div className="label">Confidence Index</div>
                <div className="val">{Math.round(data.forecast.confidence * 100)}%</div>
              </div>
              <div className="meta-item">
                <div className="label">Horizon Filter</div>
                <div className="val">24H Projection</div>
              </div>
            </div>
          </section>
        </main>

        <footer className="hud-footer">
          <div className="footer-left">
            <Share2 size={12} />
            <span>Synthetic Society Mesh: Active</span>
          </div>
          <div className="footer-right">
            <span>OSIN Project Ascension | Level 15 Mastership</span>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default CivilizationHUD;
