import React, { useState, useRef } from 'react';
import './AdvancedImageUpload.css';

interface AdvancedImageUploadProps {
  onForensicsAnalyzed: (result: any) => void;
  onClose: () => void;
}

export const AdvancedImageUpload: React.FC<AdvancedImageUploadProps> = ({ 
  onForensicsAnalyzed, 
  onClose 
}) => {
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [depth, setDepth] = useState('standard');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File) => {
    setAnalyzing(true);
    setError(null);
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('source', 'forensics_console');
    formData.append('analysis_depth', depth);

    try {
      // Direct connection to the Forensics service (mapped to 8010 in local dev)
      const response = await fetch('http://localhost:8010/forensics-analysis', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) throw new Error('Forensic audit failed');
      
      const result = await response.json();
      onForensicsAnalyzed(result);
      onClose();
    } catch (e: any) {
      setError(e.message || 'Audit Error');
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="forensics-upload-overlay">
      <div className="forensics-container">
        <div className="forensics-header">
          <div className="title-stack">
            <h3>🛡️ Deep Forensics Auditor</h3>
            <span>OSIN Strategic Verification | v2.8.0</span>
          </div>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        <div className="forensics-body">
          <div className="depth-selector">
            <span className="label">Analysis Intensity:</span>
            <div className="tabs">
              {['quick', 'standard', 'deep'].map(d => (
                <button 
                  key={d}
                  className={depth === d ? 'active' : ''}
                  onClick={() => setDepth(d)}
                >
                  {d}
                </button>
              ))}
            </div>
          </div>

          {analyzing ? (
            <div className="analyzing-state">
              <div className="scanning-line" />
              <div className="glitch-text">AUDITING_ARTEFACTS...</div>
              <div className="tools-log">
                {depth === 'deep' && <div>&gt; Running Binwalk bitstream analysis...</div>}
                <div>&gt; Correlating EXIF header integrity...</div>
                <div>&gt; Checking compression quantization tables...</div>
              </div>
            </div>
          ) : (
            <div className="drop-zone" onClick={() => fileInputRef.current?.click()}>
              <div className="icon">🛡️</div>
              <p>Drag Evidence for Forensic Audit</p>
              <span>Verify Integrity & Metadata</span>
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
        
        <div className="forensics-footer">
          Ghiro-Lite Core | ExifTool & Binwalk Enabled
        </div>
      </div>
    </div>
  );
};

export default AdvancedImageUpload;
