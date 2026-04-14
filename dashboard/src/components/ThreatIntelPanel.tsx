import React, { useState } from 'react';
import './ThreatIntelPanel.css';

interface ThreatIntelPanelProps {
  onThreatAssessmentComplete: (result: any) => void;
  onClose: () => void;
}

export const ThreatIntelPanel: React.FC<ThreatIntelPanelProps> = ({ 
  onThreatAssessmentComplete, 
  onClose 
}) => {
  const [loading, setLoading] = useState(false);
  const [target, setTarget] = useState('');
  const [error, setError] = useState<string | null>(null);

  const performAssessment = async () => {
    if (!target) return;
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8017/assess', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'X-API-Key': 'osin_master_threat_key_v350' // Placeholder for integration
        },
        body: JSON.stringify({ target: target.trim() })
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Threat assessment failed');
      }
      
      const result = await response.json();
      onThreatAssessmentComplete(result);
      onClose();
    } catch (e: any) {
      setError(e.message || 'CTI Platform Error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="threat-observer-overlay">
      <div className="threat-observer-container">
        <div className="threat-observer-header">
          <div className="title-stack">
            <h3>☣️ Cyber Threat Observatory</h3>
            <span>Internet-Scale Monitoring | Breach Intelligence | v3.5.0</span>
          </div>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        <div className="threat-observer-content">
          {loading ? (
            <div className="observing-state">
              <div className="data-spiral">
                <div className="core" />
                <div className="particle p1" />
                <div className="particle p2" />
                <div className="particle p3" />
              </div>
              <p>Scanning Internet-Scale Exposure...</p>
              <span>SpyCloud Breaches | Firecrawl Deep Web Scrapes</span>
            </div>
          ) : (
            <div className="threat-input-suite">
              <div className="threat-icon">☣️</div>
              <p>Initialize Proactive Threat Identification</p>
              
              <div className="input-box">
                <input 
                  type="text" 
                  placeholder="Target Infrastructure (Domain / IP)"
                  value={target}
                  onChange={e => setTarget(e.target.value)}
                  onKeyPress={e => e.key === 'Enter' && performAssessment()}
                />
              </div>

              <button 
                className="launch-btn" 
                onClick={performAssessment}
                disabled={!target}
              >
                Launch Multi-Source Assessment
              </button>
            </div>
          )}

          {error && <div className="threat-alert">{error}</div>}
        </div>
        
        <div className="threat-observer-footer">
          Lawful Monitoring Framework | Defensive Situational Awareness Only
        </div>
      </div>
    </div>
  );
};

export default ThreatIntelPanel;
