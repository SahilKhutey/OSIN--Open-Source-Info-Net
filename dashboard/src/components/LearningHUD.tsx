import React, { useState, useEffect, useCallback } from 'react';
import { 
  GraduationCap, 
  Database, 
  GitMerge, 
  TrendingUp, 
  Activity, 
  Sparkles,
  ChevronRight,
  Target,
  Clock
} from 'lucide-react';
import './LearningHUD.css';

interface LearningHUDProps {
  onClose: () => void;
}

export const LearningHUD: React.FC<LearningHUDProps> = ({ onClose }) => {
  const [data, setData] = useState<any>({ 
    status: 'OPTIMIZING', 
    trend: { trend: 'STABLE' },
    performance: { prediction_accuracy: 0, causal_confidence: 0, memory_relevance: 0 },
    memory_stats: { causal_links: 0 }
  });
  const [causalLinks, setCausalLinks] = useState<any>({});

  const fetchData = useCallback(async () => {
    try {
      const [sRes, gRes] = await Promise.all([
        fetch('http://localhost:8023/status'),
        fetch('http://localhost:8023/causal-graph')
      ]);
      const sData = await sRes.json();
      const gData = await gRes.json();
      setData(sData);
      setCausalLinks(gData);
    } catch (err) {
      console.error('Learning sync failed:', err);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, [fetchData]);

  return (
    <div className="learning-overlay">
      <div className="learning-hud">
        {/* Header: OSIN Subconscious */}
        <header className="hud-header">
          <div className="hud-branding">
            <GraduationCap className="icon-glow" size={24} />
            <div className="title-stack">
              <h1>OSIN Learning Organism</h1>
              <span>Cognitive Subconscious | Self-Evolving v6.0.0</span>
            </div>
          </div>
          <div className="hud-meta">
            <div className="status-badge">
              <Sparkles size={14} />
              <span>{data.status}</span>
            </div>
            <button className="close-btn" onClick={onClose}>×</button>
          </div>
        </header>

        <main className="hud-content">
          {/* Column 1: Performance Trajectory */}
          <section className="hud-panel perf-panel">
            <div className="panel-label">
              <TrendingUp size={14} />
              <span>Learning Trajectory</span>
            </div>
            <div className="trend-banner">
              <span className="label">Evolutionary Trend:</span>
              <span className={`val ${data.trend.trend.toLowerCase()}`}>{data.trend.trend}</span>
            </div>
            <div className="metrics-grid">
              {Object.entries(data.performance).map(([key, val]: [string, any]) => (
                <div className="metric-item" key={key}>
                  <div className="metric-header">
                    <span className="key">{key.replace('_', ' ')}</span>
                    <span className="val">{Math.round(val * 100)}%</span>
                  </div>
                  <div className="metric-bar">
                    <div className="fill" style={{ width: `${val * 100}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Column 2: Causal Linkages */}
          <section className="hud-panel causal-panel">
            <div className="panel-label">
              <GitMerge size={14} />
              <span>Causal Relationship Subconscious</span>
            </div>
            <div className="causal-stats">
              <div className="stat-box">
                <span className="val">{data.memory_stats.causal_links}</span>
                <span className="label">Inferred Links</span>
              </div>
            </div>
            <div className="causal-list">
              {Object.values(causalLinks).slice(-8).map((link: any, i: number) => (
                <div className="causal-item" key={i}>
                  <div className="node-link">
                    <Target size={12} color="#4cd137" />
                    <span className="id">{link.source.slice(8, 16)}</span>
                    <ChevronRight size={10} color="#00ffcc" />
                    <span className="effect">{link.relation}</span>
                    <ChevronRight size={10} color="#00ffcc" />
                    <span className="id">{link.target.slice(8, 16)}</span>
                  </div>
                  <div className="conf-badge">CONF: {Math.round(link.confidence * 100)}%</div>
                </div>
              ))}
              {Object.values(causalLinks).length === 0 && (
                <div className="empty-msg">Waiting for causal emergence...</div>
              )}
            </div>
          </section>

          {/* Column 3: Memory Depth */}
          <section className="hud-panel memory-panel">
            <div className="panel-label">
              <Database size={14} />
              <span>Persistent Intelligence Memory</span>
            </div>
            <div className="memory-visualization">
              <div className="brain-map">
                {/* Simulated neural nodes */}
                <div className="neural-node pulse-slow" style={{ top: '20%', left: '30%' }}></div>
                <div className="neural-node pulse-fast" style={{ top: '50%', left: '70%' }}></div>
                <div className="neural-node pulse-med" style={{ top: '80%', left: '40%' }}></div>
                <div className="scan-sweep"></div>
                <span>PIM ACTIVE: {data.memory_stats.db_path}</span>
              </div>
            </div>
            <div className="memory-info">
              <div className="info-row">
                <Activity size={12} />
                <span>Episodic Consolidation: Optimal</span>
              </div>
              <div className="info-row">
                <Clock size={12} />
                <span>Memory Retention: 90 Days</span>
              </div>
            </div>
          </section>
        </main>

        <footer className="hud-footer">
          <div className="footer-left">
            <TrendingUp size={12} />
            <span>Reinforcement Learning Cycle: Active (k=0.02)</span>
          </div>
          <div className="footer-right">
            <span>Cognitive Transcendence Level: Phase 6</span>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default LearningHUD;
