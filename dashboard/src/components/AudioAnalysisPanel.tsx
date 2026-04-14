import React, { useState, useRef } from 'react';
import './AudioAnalysisPanel.css';

interface AudioAnalysisPanelProps {
  onAudioAnalyzed: (result: any) => void;
  onClose: () => void;
}

export const AudioAnalysisPanel: React.FC<AudioAnalysisPanelProps> = ({ 
  onAudioAnalyzed, 
  onClose 
}) => {
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File) => {
    setAnalyzing(true);
    setError(null);
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('source', 'operator_audint');

    try {
      // Direct connection to the Audio Intel service (mapped to 8012 in local dev)
      const response = await fetch('http://localhost:8012/analyze-audio', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) throw new Error('Acoustic audit failed');
      
      const result = await response.json();
      onAudioAnalyzed(result);
      onClose();
    } catch (e: any) {
      setError(e.message || 'AUDINT Error');
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="audio-panel-overlay">
      <div className="audio-container">
        <div className="audio-header">
          <div className="title-stack">
            <h3>🎵 Audio Intelligence (AUDINT)</h3>
            <span>Acoustic Signature Analysis | v3.0.0</span>
          </div>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        <div className="audio-body">
          {analyzing ? (
            <div className="analyzing-state">
              <div className="oscilloscope-hud">
                <div className="wave-trace" />
                <div className="wave-trace delay" />
              </div>
              <p>Analyzing Spectral Centroids...</p>
            </div>
          ) : (
            <div className="drop-zone-audio" onClick={() => fileInputRef.current?.click()}>
              <div className="icon">🔊</div>
              <p>Drag Acoustic Evidence Here</p>
              <span>Supported: WAV, MP3, FLAC</span>
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
        
        <div className="audio-footer">
          Librosa 0.10.0 | Spectral Auditing Active
        </div>
      </div>
    </div>
  );
};

export default AudioAnalysisPanel;
