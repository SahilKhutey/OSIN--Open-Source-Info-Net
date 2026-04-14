import React, { useState } from 'react';
import './AdvancedCyberPanel.css';

interface AdvancedCyberPanelProps {
  onAdvancedScanComplete: (result: any) => void;
  onClose: () => void;
}

export const AdvancedCyberPanel: React.FC<AdvancedCyberPanelProps> = ({ 
  onAdvancedScanComplete, 
  onClose 
}) => {
  const [scanning, setScanning] = useState(false);
  const [target, setTarget] = useState('');
  const [scanType, setScanType] = useState('standard');
  const [error, setError] = useState<string | null>(null);

  const startScan = async () => {
    if (!target) return;
    setScanning(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8015/advanced-scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          target: target.trim(),
          scan_type: scanType,
          dns_enum: true,
          port_scan: true,
          shodan_query: true,
          osint_collect: scanType === 'comprehensive'
        })
      });

      if (!response.ok) throw new Error('Advanced reconnaissance failed');
      
      const result = await response.json();
      onAdvancedScanComplete(result);
      onClose();
    } catch (e: any) {
      setError(e.message || 'Pro-Recon Error');
    } finally {
      setScanning(false);
    }
  };

  return (
    <div className="pro-recon-overlay">
      <div className="pro-recon-container">
        <div className="pro-recon-header">
          <div className="title-stack">
            <h3>⚡ PRO Cyber Recon</h3>
            <span>Recon-ng | Nmap Scripting Engine | v3.3.0</span>
          </div>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        <div className="pro-recon-body">
          {scanning ? (
            <div className="scanning-state">
              <div className="radar-hud">
                <div className="sweep" />
                <div className="grid-overlay" />
              </div>
              <p>Executing {scanType.toUpperCase()} Audit...</p>
              <span>Nmap NSE | DNS Brute Force | IP Geolocation</span>
            </div>
          ) : (
            <div className="pro-recon-input">
              <div className="profile-selector">
                {['quick', 'standard', 'comprehensive'].map(type => (
                  <button 
                    key={type}
                    className={scanType === type ? 'active' : ''}
                    onClick={() => setScanType(type)}
                  >
                    {type}
                  </button>
                ))}
              </div>
              
              <div className="input-group">
                <input 
                  type="text" 
                  placeholder="Target Domain / CIDR / IP"
                  value={target}
                  onChange={e => setTarget(e.target.value)}
                  onKeyPress={e => e.key === 'Enter' && startScan()}
                />
              </div>

              <button 
                className="execute-btn" 
                onClick={startScan}
                disabled={!target}
              >
                Launch Professional Recon
              </button>
            </div>
          )}

          {error && <div className="error-msg">{error}</div>}
        </div>
        
        <div className="pro-recon-footer">
          Vulnerability Scanning Enabled | NSE Vuln Scripts Active
        </div>
      </div>
    </div>
  );
};

export default AdvancedCyberPanel;
