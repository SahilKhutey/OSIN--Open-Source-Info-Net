import React, { useState } from 'react';
import './WeatherControls.css';

interface WeatherLayerInfo {
  name: string;
  tile_url: string;
  opacity: number;
}

interface WeatherControlsProps {
  weatherData: {
    weather_layers: Record<string, WeatherLayerInfo>;
    current_weather?: {
      temp: number;
      conditions: string;
      wind_speed: number;
    };
    severe_alerts: { event: string; severity: string }[];
  };
  onLayerChange: (layerKey: string | null) => void;
  onOpacityChange: (opacity: number) => void;
  onClose: () => void;
}

export const WeatherControls: React.FC<WeatherControlsProps> = ({ 
  weatherData, 
  onLayerChange, 
  onOpacityChange,
  onClose 
}) => {
  const [activeLayer, setActiveLayer] = useState<string | null>(null);
  const [opacity, setOpacity] = useState(0.6);

  const toggleLayer = (key: string) => {
    const newLayer = activeLayer === key ? null : key;
    setActiveLayer(newLayer);
    onLayerChange(newLayer);
  };

  const handleOpacity = (val: number) => {
    setOpacity(val);
    onOpacityChange(val);
  };

  return (
    <div className="weather-controls-panel">
      <div className="weather-header">
        <h3>💨 Weather Intelligence</h3>
        <button className="close-btn" onClick={onClose}>×</button>
      </div>

      <div className="weather-content">
        {/* Current Telemetry */}
        {weatherData.current_weather && (
          <div className="telemetry-box">
            <div className="telemetry-main">
              <span className="temp">{Math.round(weatherData.current_weather.temp)}°C</span>
              <span className="desc">{weatherData.current_weather.conditions}</span>
            </div>
            <div className="telemetry-sub">
              Wind: {weatherData.current_weather.wind_speed} m/s
            </div>
          </div>
        )}

        {/* Severe Alerts */}
        {weatherData.severe_alerts.length > 0 && (
          <div className="alerts-box">
            <div className="alerts-title">⚠️ Severe Alerts</div>
            {weatherData.severe_alerts.map((alert, idx) => (
              <div key={idx} className={`alert-item ${alert.severity.toLowerCase()}`}>
                <div className="alert-event">{alert.event}</div>
                <div className="alert-sev">{alert.severity}</div>
              </div>
            ))}
          </div>
        )}

        {/* Layer Selection */}
        <div className="layers-section">
          <div className="section-title">Atmospheric Layers</div>
          <div className="layers-list">
            {Object.entries(weatherData.weather_layers).map(([key, layer]) => (
              <button 
                key={key}
                className={`layer-btn ${activeLayer === key ? 'active' : ''}`}
                onClick={() => toggleLayer(key)}
              >
                {layer.name}
              </button>
            ))}
          </div>
        </div>

        {/* Opacity Control */}
        {activeLayer && (
          <div className="opacity-section">
            <div className="section-title">Overlay Alpha</div>
            <input 
              type="range" 
              min="0" 
              max="1" 
              step="0.1" 
              value={opacity} 
              onChange={(e) => handleOpacity(parseFloat(e.target.value))}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default WeatherControls;
