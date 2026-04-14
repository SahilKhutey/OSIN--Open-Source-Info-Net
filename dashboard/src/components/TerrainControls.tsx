import React, { useState } from 'react';
import './TerrainControls.css';

interface TerrainControlsProps {
  topoData: {
    elevation_data?: {
      center: number;
      min: number;
      max: number;
    };
    terrain_analysis: {
      slope: {
        max_slope_deg: number;
        is_mountainous: boolean;
      };
    };
    risk_assessment: Record<string, number>;
  };
  onOpacityChange: (opacity: number) => void;
  onToggleTerrain: () => void;
  onClose: () => void;
}

export const TerrainControls: React.FC<TerrainControlsProps> = ({ 
  topoData, 
  onOpacityChange, 
  onToggleTerrain,
  onClose 
}) => {
  const [opacity, setOpacity] = useState(0.8);
  const [showDetails, setShowDetails] = useState(false);

  const handleOpacity = (val: number) => {
    setOpacity(val);
    onOpacityChange(val);
  };

  const getRiskLabel = (val: number) => {
    if (val > 0.7) return 'high';
    if (val > 0.3) return 'medium';
    return 'low';
  };

  return (
    <div className="terrain-controls-panel">
      <div className="panel-header">
        <h3>🏔️ Terrain Intelligence</h3>
        <button className="close-btn" onClick={onClose}>×</button>
      </div>

      <div className="panel-content">
        {/* Elevation Metrics */}
        {topoData.elevation_data && (
          <div className="metrics-section">
            <div className="main-elevation">
              <span className="elev-value">{Math.round(topoData.elevation_data.center)}m</span>
              <span className="elev-label">Altitude</span>
            </div>
            <div className="elev-stats">
              <div className="stat">Min: {Math.round(topoData.elevation_data.min)}m</div>
              <div className="stat">Max: {Math.round(topoData.elevation_data.max)}m</div>
            </div>
          </div>
        )}

        {/* Slope Analysis */}
        <div className="slope-section">
          <div className="slope-header">
            <span>Terrain Grading</span>
            <span className={`tag ${topoData.terrain_analysis.slope.is_mountainous ? 'mountain' : 'flat'}`}>
              {topoData.terrain_analysis.slope.is_mountainous ? 'Rugged' : 'Stable'}
            </span>
          </div>
          <div className="slope-value">
            {topoData.terrain_analysis.slope.max_slope_deg.toFixed(1)}° Grade
          </div>
        </div>

        {/* Risk Assessment */}
        <div className="risks-section">
          <div className="section-title">Enviro-Tactical Risks</div>
          {Object.entries(topoData.risk_assessment).map(([risk, val]) => (
            <div key={risk} className="risk-row">
              <div className="risk-info">
                <span className="risk-name">{risk.replace('_', ' ')}</span>
                <span className="risk-pct">{Math.round(val * 100)}%</span>
              </div>
              <div className="risk-track">
                <div 
                  className={`risk-fill ${getRiskLabel(val)}`}
                  style={{ width: `${val * 100}%` }}
                />
              </div>
            </div>
          ))}
        </div>

        {/* Action Controls */}
        <div className="controls-footer">
          <button className="action-btn toggle" onClick={onToggleTerrain}>
            Toggle Displacement Map
          </button>
          
          <div className="alpha-control">
            <span>Opacity</span>
            <input 
              type="range" 
              min="0" 
              max="1" 
              step="0.1" 
              value={opacity} 
              onChange={(e) => handleOpacity(parseFloat(e.target.value))}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default TerrainControls;
