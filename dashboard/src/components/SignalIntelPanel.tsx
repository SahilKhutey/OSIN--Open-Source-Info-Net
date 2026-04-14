import React, { useState } from 'react';
import './SignalIntelPanel.css';

interface SignalIntelPanelProps {
  onSignalScanComplete: (result: any) => void;
  onClose: () => void;
}

export const SignalIntelPanel: React.FC<SignalIntelPanelProps> = ({ 
  onSignalScanComplete, 
  onClose 
}) => {
  const [scanning, setScanning] = useState(false);
  const [target, setTarget] = useState('');
  const [scanType, setScanType] = useState('comprehensive');
  const [error, setError] = useState<string | null>(null);

  const startScan = async () => {
    if (!target) return;
    setScanning(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8016/signal-scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          target: target.trim(),
          intel_type: scanType,
          include_emails: true,
          include_leaks: true
        })
      });

      if (!response.ok) throw new Error('Signal intelligence gathering failed');
      
      const result = await response.json();
      onSignalScanComplete(result);
      onClose();
    } catch (e: any) {
      setError(e.message || 'Signal Error');
    } finally {
      setScanning(false);
    }
  };

  return (
    <div className="signal-panel-overlay">
      <div className="signal-container">
        <div className="signal-header">
          <div className="title-stack">
            <h3>📡 Signal & Leak Intel</h3>
            <span>SIGINT + LEAKINT Strategic Core | v3.4.0</span>
          </div>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        <div className="signal-body">
          {scanning ? (
            <div className="scanning-state">
              <div className="signal-hud">
                <div className="wave wave1" />
                <div className="wave wave2" />
                <div className="wave wave3" />
              </div>
              <p>Auditing Signal Clusters...</p>
              <span>IntelX | theHarvester | Metagoofil Discovery</span>
            </div>
          ) : (
            <div className="signal-input-area">
              <div className="icon">📡</div>
              <p>Initialize Signal Identification</p>
              
              <div className="scan-modes">
                {['basic', 'comprehensive', 'targeted'].map(mode => (
                  <button 
                    key={mode} 
                    className={scanType === mode ? 'active' : ''}
                    onClick={() => setScanType(mode)}
                  >
                    {mode}
                  </button>
                ))}
              </div>

              <input 
                type="text" 
                placeholder="Domain / Email / Subject"
                value={target}
                onChange={e => setTarget(e.target.value)}
                onKeyPress={e => e.key === 'Enter' && startScan()}
              />
              <button 
                className="audit-btn" 
                onClick={startScan}
                disabled={!target}
              >
                Launch Signal Collection
              </button>
            </div>
          )}

          {error && <div className="error-alert">{error}</div>}
        </div>
        
        <div className="signal-footer">
          WiFi Geolocation | Credential Leak Check | Active Monitoring
        </div>
      </div>
    </div>
  );
};

export default SignalIntelPanel;
