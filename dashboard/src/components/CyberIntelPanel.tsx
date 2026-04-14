import React, { useState } from 'react';
import './CyberIntelPanel.css';

interface CyberIntelPanelProps {
  onCyberAnalysisComplete: (result: any) => void;
  onClose: () => void;
}

export const CyberIntelPanel: React.FC<CyberIntelPanelProps> = ({ 
  onCyberAnalysisComplete, 
  onClose 
}) => {
  const [analyzing, setAnalyzing] = useState(false);
  const [target, setTarget] = useState('');
  const [error, setError] = useState<string | null>(null);

  const startAnalysis = async () => {
    if (!target) return;
    setAnalyzing(true);
    setError(null);

    try {
      // Direct connection to the Cyber Intel service (mapped to 8014 in local dev)
      const response = await fetch('http://localhost:8014/analyze-cyber', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          target: target.trim(),
          analysis_type: 'standard',
          include_active: false
        })
      });

      if (!response.ok) throw new Error('Cyber reconnaissance failed');
      
      const result = await response.json();
      onCyberAnalysisComplete(result);
      onClose();
    } catch (e: any) {
      setError(e.message || 'CYBINT Error');
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="cyber-panel-overlay">
      <div className="cyber-container">
        <div className="cyber-header">
          <div className="title-stack">
            <h3>🛡️ Cyber Intelligence (CYBINT)</h3>
            <span>Reconnaissance & Asset Audit | v3.2.0</span>
          </div>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        <div className="cyber-body">
          {analyzing ? (
            <div className="analyzing-state">
              <div className="binary-hud">
                <div className="bit-stream">0101101001011010110...</div>
                <div className="scanner-line" />
              </div>
              <p>Enumerating DNS Infrastructure...</p>
            </div>
          ) : (
            <div className="recon-input-area">
              <div className="icon">🌐</div>
              <p>Identify Digital Target</p>
              <input 
                type="text" 
                placeholder="domain.com / IP Address"
                value={target}
                onChange={e => setTarget(e.target.value)}
                onKeyPress={e => e.key === 'Enter' && startAnalysis()}
              />
              <button 
                className="audit-btn" 
                onClick={startAnalysis}
                disabled={!target}
              >
                Initialize Recon Audit
              </button>
            </div>
          )}

          {error && <div className="error-alert">{error}</div>}
        </div>
        
        <div className="cyber-footer">
          WHOIS | Amass | DNS Recursor Active
        </div>
      </div>
    </div>
  );
};

export default CyberIntelPanel;
