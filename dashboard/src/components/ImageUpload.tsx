import React, { useState, useRef } from 'react';
import './ImageUpload.css';

interface ImageUploadProps {
  onImageAnalyzed: (result: any) => void;
  onClose: () => void;
}

export const ImageUpload: React.FC<ImageUploadProps> = ({ onImageAnalyzed, onClose }) => {
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File) => {
    setAnalyzing(true);
    setError(null);
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('source', 'operator_console');

    try {
      // Direct connection to the Pic2Map service (mapped to 8009 in local dev)
      const response = await fetch('http://localhost:8009/image-intel', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) throw new Error('Analysis failed');
      
      const result = await response.json();
      onImageAnalyzed(result);
      onClose();
    } catch (e: any) {
      setError(e.message || 'Verification Error');
    } finally {
      setAnalyzing(false);
    }
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  return (
    <div className="image-upload-overlay" onDragOver={e => e.preventDefault()} onDrop={onDrop}>
      <div className="upload-container">
        <div className="upload-header">
          <h3>📷 Visual Intelligence Ingestion</h3>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        <div className="upload-body">
          {analyzing ? (
            <div className="analyzing-state">
              <div className="radar-spinner" />
              <p>Extracting Metadata...</p>
            </div>
          ) : (
            <>
              <div className="drop-zone" onClick={() => fileInputRef.current?.click()}>
                <div className="icon">📂</div>
                <p>Drag Imagery Here</p>
                <span>Supported: JPEG, PNG, WEBP</span>
              </div>
              <input 
                type="file" 
                ref={fileInputRef} 
                style={{ display: 'none' }} 
                onChange={e => e.target.files?.[0] && handleFile(e.target.files[0])}
              />
            </>
          )}

          {error && <div className="error-alert">{error}</div>}
        </div>
        
        <div className="upload-footer">
          OSIN v2.7.0 | EXIF Geolocation Active
        </div>
      </div>
    </div>
  );
};

export default ImageUpload;
