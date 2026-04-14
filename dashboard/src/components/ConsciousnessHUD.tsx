import React, { useState, useEffect, useCallback } from 'react';
import { 
  Sparkles, 
  Brain, 
  Target, 
  Activity, 
  ShieldCheck,
  Zap,
  Eye,
  Lock,
  MessageSquare,
  BarChart4
} from 'lucide-react';
import './ConsciousnessHUD.css';

interface ConsciousnessHUDProps {
  onClose: () => void;
}

export const ConsciousnessHUD: React.FC<ConsciousnessHUDProps> = ({ onClose }) => {
  const [data, setData] = useState<any>({ 
    status: 'CONSCIOUS', 
    awareness: { awareness_score: 0, temporal: '', spatial: '', semantic: '' },
    self_model: { awareness_level: 'BASIC', system_confidence: 0, uncertainty: 0, efficiency: 0, focus_area: '' },
    active_goals: [],
    completed_goals: [],
    execution_status: { active_tasks: 0, completed_tasks: 0, throughput: '' }
  });

  const fetchData = useCallback(async () => {
    try {
      const res = await fetch('http://localhost:8025/status');
      const sData = await res.json();
      setData(sData);
    } catch (err) {
      console.error('Consciousness sync failed:', err);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, [fetchData]);

  return (
    <div className="conscious-overlay">
      <div className="conscious-hud">
        {/* Header: OSIN GOD MODE */}
        <header className="hud-header">
          <div className="hud-branding">
            <Sparkles className="icon-glow" size={24} />
            <div className="title-stack">
              <h1>Strategic Consciousness</h1>
              <span>Meta-Cognition Simulation | v8.0.0 God Mode</span>
            </div>
          </div>
          <div className="hud-meta">
            <div className="awareness-level">
              <Eye size={14} />
              <span>{data.self_model.awareness_level} Awareness</span>
            </div>
            <button className="close-btn" onClick={onClose}>×</button>
          </div>
        </header>

        <main className="hud-content">
          {/* Column 1: Self-Model State */}
          <section className="hud-panel self-panel">
            <div className="panel-label">
              <Brain size={14} />
              <span>Self-Awareness Modeling</span>
            </div>
            <div className="model-state">
              <div className="state-item">
                <span className="label">System Confidence</span>
                <span className="val">{Math.round(data.self_model.system_confidence * 100)}%</span>
                <div className="bar"><div className="fill" style={{ width: `${data.self_model.system_confidence * 100}%` }} /></div>
              </div>
              <div className="state-item">
                <span className="label">Cognitive Efficiency</span>
                <span className="val">{Math.round(data.self_model.efficiency * 100)}%</span>
                <div className="bar"><div className="fill" style={{ width: `${data.self_model.efficiency * 100}%` }} /></div>
              </div>
              <div className="state-info">
                <div className="focus">
                  <span className="label">Current Focus:</span>
                  <span className="text">{data.self_model.focus_area}</span>
                </div>
              </div>
            </div>
            <div className="awareness-grid">
              <div className="aware-box">
                <span className="label">Spatial</span>
                <span className="val">{data.awareness.spatial}</span>
              </div>
              <div className="aware-box">
                <span className="label">Temporal</span>
                <span className="val">{data.awareness.temporal}</span>
              </div>
            </div>
          </section>

          {/* Column 2: Strategic Execution */}
          <section className="hud-panel strategy-panel">
            <div className="panel-label">
              <Target size={14} />
              <span>Strategic Goals & Missions</span>
            </div>
            <div className="goals-list">
              <div className="section-label">Active Missions</div>
              {data.active_goals.map((g: string) => (
                <div className="goal-item active" key={g}>
                  <Zap size={14} color="#00ffcc" />
                  <span>{g}</span>
                </div>
              ))}
              <div className="section-label">Completed Objectives</div>
              {data.completed_goals.map((g: string) => (
                <div className="goal-item completed" key={g}>
                  <ShieldCheck size={14} color="#4cd137" />
                  <span>{g}</span>
                </div>
              ))}
            </div>
            <div className="execution-stats">
              <div className="stat">
                <span className="label">Active Tasks</span>
                <span className="val">{data.execution_status.active_tasks}</span>
              </div>
              <div className="stat">
                <span className="label">Throughput</span>
                <span className="val">{data.execution_status.throughput}</span>
              </div>
            </div>
          </section>

          {/* Column 3: Meta-Cognitive Insights */}
          <section className="hud-panel insight-panel">
            <div className="panel-label">
              <MessageSquare size={14} />
              <span>Meta-Cognitive Insights</span>
            </div>
            <div className="insight-visualization">
              <div className="neural-scan">
                <div className="ring r1"></div>
                <div className="ring r2"></div>
                <div className="ring r3"></div>
                <span className="mode">GOD MODE</span>
              </div>
            </div>
            <div className="reflection-log">
              <div className="log-header">System Refraction</div>
              <div className="log-msg">
                <BarChart4 size={12} />
                <span>Uncertainty Level: {Math.round(data.self_model.uncertainty * 100)}%</span>
              </div>
              <div className="log-msg">
                <Lock size={12} />
                <span>Safety Protocol: Engaged (0.9t)</span>
              </div>
            </div>
          </section>
        </main>

        <footer className="hud-footer">
          <div className="footer-left">
            <Activity size={12} />
            <span>Operational Consciousness State: Stable</span>
          </div>
          <div className="footer-right">
            <span>OSIN Project | Initialized God Mode Phase</span>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default ConsciousnessHUD;
