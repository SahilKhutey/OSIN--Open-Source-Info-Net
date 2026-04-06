import React, { useEffect, useRef, useState } from 'react';
import Globe from 'react-globe.gl';
import { useStore } from '../store/useStore';
import '../styles/HeatmapGlobe.css';

interface HeatmapData {
  lat: number;
  lng: number;
  value: number;
}

export const HeatmapGlobe: React.FC = () => {
  const globeRef = useRef<any>(null);
  const [heatmapData, setHeatmapData] = useState<HeatmapData[]>([]);
  const events = useStore((state) => state.events);

  useEffect(() => {
    // Aggregate events by location for heatmap
    const locationMap = new Map<string, number>();

    events.forEach((event) => {
      if (event.location) {
        const key = `${Math.round(event.location.lat * 10) / 10},${Math.round(event.location.lng * 10) / 10}`;
        locationMap.set(key, (locationMap.get(key) || 0) + 1);
      }
    });

    const data: HeatmapData[] = Array.from(locationMap, ([key, value]) => {
      const [lat, lng] = key.split(',').map(Number);
      return { lat, lng, value };
    });

    setHeatmapData(data);

    if (globeRef.current) {
      globeRef.current.controls().autoRotate = true;
      globeRef.current.controls().autoRotateSpeed = 1.5;
    }
  }, [events]);

  return (
    <div className="heatmap-container">
      <div className="heatmap-header">
        <h2>INTELLIGENCE DENSITY MAP</h2>
        <span className="heatmap-mode-indicator">HEATMAP MODE</span>
      </div>

      <Globe
        ref={globeRef}
        globeImageUrl="//cdn.jsdelivr.net/npm/three-globe/example/img/earth-night.jpg"
        hexBinPointsData={heatmapData}
        hexBinPointWeight="value"
        hexBinResolution={4}
        hexBinMargin={0.7}
        hexLabel="value"
        hexColor={(d: any) => {
          const scale = Math.max(1, (d?.value || 1) / 10);
          return `rgba(0, 255, 0, ${Math.min(0.8, scale * 0.2)})`;
        }}
      />

      <div className="heatmap-info">
        <p>Intelligence signal concentration across regions</p>
        <div className="intensity-scale">
          <span className="label">Low</span>
          <div className="gradient-bar"></div>
          <span className="label">High</span>
        </div>
      </div>
    </div>
  );
};
