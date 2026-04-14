import React, { useState, useRef } from 'react';
import './AdvancedForensicsPanel.css';

interface AdvancedForensicsPanelProps {
  onForensicsComplete: (result: any) => void;
  onClose: () => void;
}

export const AdvancedForensicsPanel: React.FC<AdvancedForensicsPanelProps> = ({ 
  onForensicsComplete, 
  onClose 
}) => {
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mode, setMode] = useState('complete');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File) => {
    setAnalyzing(true);
    setError(null);
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('analysis_mode', mode);

    try {
      // Direct connection to the Forensics Pro service (mapped to 8011 in local dev)
      const response = await fetch('http://localhost:8011/analyze-forensics', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) throw new Error('Unified Pro audit failed');
      
      const result = await response.json();
      onForensicsComplete(result);
      onClose();
    } catch (e: any) {
      setError(e.message || 'Pro Audit Error');
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="pro-forensics-overlay">
      <div className="pro-container">
        <div className="pro-header">
          <div className="title-stack">
            <h3>👁️ Unified Forensics Engine</h3>
            <span>DFINT Strategic Capability | v2.9.0</span>
          </div>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        <div className="pro-body">
          <div className="mode-selector">
            <span className="label">Analysis Method:</span>
            <div className="pills">
              {['quick', 'standard', 'complete'].map(m => (
                <button 
                  key={m}
                  className={mode === m ? 'active' : ''}
                  onClick={() => setMode(m)}
                >
                  {m}
                </button>
              ))}
            </div>
          </div>

          {analyzing ? (
            <div className="analyzing-state">
              <div className="cv-hud">
                <div className="crosshair" />
                <div className="scan-line" />
              </div>
              <div className="status-log">
                <div>&gt; DECODING_BITSTREAM...</div>
                <div>&gt; CALCULATING_ELA_MAPS...</div>
                <div>&gt; IDENTIFYING_CLONE_KEYPOINTS... (SIFT)</div>
                <div>&gt; ESTIMATING_AUTHENTICITY_INDEX...</div>
              </div>
            </div>
          ) : (
            <div className="drop-zone-pro" onClick={() => fileInputRef.current?.click()}>
              <div className="icon">🛡️</div>
              <p>Initialize Advanced DFINT Audit</p>
              <span>Error Level Analysis & Keypoint Correlation</span>
            </div>
          )}
          
          <input 
            type="file" 
            ref={fileInputRef} 
            style={{ display: 'none' }} 
            onChange={e => e.target.files?.[0] && handleFile(e.target.files[0])}
          />

          {error && <div className="error-alert">{error}</div>}
        </div>
        
        <div className="pro-footer">
          OpenCV Headless | PIL | OSIN Unified v2.9.0
        </div>
      </div>
    </div>
  );
};

export default AdvancedForensicsPanel;
