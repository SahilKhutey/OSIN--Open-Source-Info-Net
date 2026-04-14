import React, { useState, useEffect } from 'react';
import { useStore } from '../store/useStore';
import './StreetViewPanel.css';

interface StreetImage {
  id: string;
  thumb_256_url: string;
  thumb_1024_url: string;
  captured_at: string;
  distance_m: number;
}

interface StreetViewPanelProps {
  eventId: string;
  onClose: () => void;
}

export const StreetViewPanel: React.FC<StreetViewPanelProps> = ({ eventId, onClose }) => {
  const { events } = useStore();
  const event = events.find(e => e.id === eventId);
  
  const [images, setImages] = useState<StreetImage[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (event?.street_intel?.images) {
      setImages(event.street_intel.images);
      setCurrentIndex(0);
    }
  }, [event]);

  const nextImage = () => {
    if (images.length === 0) return;
    setCurrentIndex((prev) => (prev + 1) % images.length);
  };

  const prevImage = () => {
    if (images.length === 0) return;
    setCurrentIndex((prev) => (prev - 1 + images.length) % images.length);
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return 'Unknown date';
    return new Date(dateString).toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (!event) return null;

  const selectedImage = images[currentIndex];

  return (
    <div className="street-view-panel">
      <div className="panel-header">
        <h3>
          <span className="icon">📷</span> Ground Truth Intelligence
        </h3>
        <button className="close-btn" onClick={onClose}>×</button>
      </div>

      <div className="panel-content">
        {loading ? (
          <div className="status-msg">Loading street metadata...</div>
        ) : images.length === 0 ? (
          <div className="status-msg no-coverage">
            <p>No street-level imagery available for this location.</p>
            <div className="hint">Try searching a different event or timeframe.</div>
          </div>
        ) : (
          <div className="image-viewer">
            <div className="main-image-container">
              <img 
                src={selectedImage?.thumb_1024_url} 
                alt="Street view" 
                className="street-image"
              />
              <div className="image-metadata">
                <div className="capture-info">
                  <span className="label">Captured:</span> {formatDate(selectedImage?.captured_at)}
                </div>
                <div className="distance-info">
                  <span className="label">Proximity:</span> {Math.round(selectedImage?.distance_m || 0)}m
                </div>
              </div>
            </div>

            <div className="viewer-controls">
              <button className="nav-btn" onClick={prevImage} disabled={images.length <= 1}>◀</button>
              <div className="image-counter">
                Image {currentIndex + 1} of {images.length}
              </div>
              <button className="nav-btn" onClick={nextImage} disabled={images.length <= 1}>▶</button>
            </div>

            <div className="thumbnail-strip">
              {images.map((img, idx) => (
                <div 
                  key={img.id}
                  className={`thumbnail-wrapper ${idx === currentIndex ? 'active' : ''}`}
                  onClick={() => setCurrentIndex(idx)}
                >
                  <img src={img.thumb_256_url} alt="Thumbnail" />
                </div>
              ))}
            </div>

            <div className="analytics-box">
              <div className="analytics-header">Confidence Correlation</div>
              <div className="analytics-grid">
                <div className="metric">
                  <div className="metric-label">Quality</div>
                  <div className="metric-value">{(event.street_intel?.coverage_quality * 100).toFixed(0)}%</div>
                </div>
                <div className="metric">
                  <div className="metric-label">Impact</div>
                  <div className="metric-value">
                    +{(event.street_intel?.confidence_impact - event.confidence).toFixed(2)}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default StreetViewPanel;
