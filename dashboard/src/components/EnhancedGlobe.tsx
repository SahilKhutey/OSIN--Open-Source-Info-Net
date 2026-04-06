import React, { useEffect, useRef, useState } from 'react';
import Globe from 'react-globe.gl';
import { useStore } from '../store/useStore';
import '../styles/EnhancedGlobe.css';

interface GlobePoint {
  lat: number;
  lng: number;
  color: string;
  size: number;
  value: number;
  label?: string;
}

export const EnhancedGlobe: React.FC = () => {
  const globeRef = useRef<any>(null);
  const [globeData, setGlobeData] = useState<GlobePoint[]>([]);
  const events = useStore((state) => state.events);

  useEffect(() => {
    // Convert events to globe data points
    const points: GlobePoint[] = events
      .filter((event) => event.location)
      .map((event) => ({
        lat: event.location!.lat,
        lng: event.location!.lng,
        color: getSeverityColor(event.severity),
        size: getSeveritySize(event.severity),
        value: 1,
        label: event.location?.country,
      }));

    setGlobeData(points);

    // Auto-rotate globe
    if (globeRef.current) {
      globeRef.current.controls().autoRotate = true;
      globeRef.current.controls().autoRotateSpeed = 2;
    }
  }, [events]);

  const getSeverityColor = (severity: string): string => {
    switch (severity) {
      case 'critical':
        return '#ff0000';
      case 'high':
        return '#ff6600';
      case 'medium':
        return '#ffff00';
      case 'low':
        return '#00ff00';
      default:
        return '#00ffff';
    }
  };

  const getSeveritySize = (severity: string): number => {
    switch (severity) {
      case 'critical':
        return 1.5;
      case 'high':
        return 1.2;
      case 'medium':
        return 0.8;
      case 'low':
        return 0.5;
      default:
        return 0.7;
    }
  };

  return (
    <div className="globe-container">
      <div className="globe-header">
        <h2>GLOBAL INTELLIGENCE MAP</h2>
        <span className="point-count">{globeData.length} ACTIVE POINTS</span>
      </div>
      
      <Globe
        ref={globeRef}
        globeImageUrl="//cdn.jsdelivr.net/npm/three-globe/example/img/earth-night.jpg"
        bumpImageUrl="//cdn.jsdelivr.net/npm/three-globe/example/img/earth-topology.png"
        pointsData={globeData}
        pointAltitude={0.01}
        pointColor="color"
        pointSize="size"
        pointLabel="label"
        pointResolution={4}
        onPointHover={(d: any) => {
          if (globeRef.current) {
            globeRef.current.pointOfView({ lat: d?.lat, lng: d?.lng, altitude: 2.5 }, 1000);
          }
        }}
      />

      <div className="globe-legend">
        <div className="legend-item">
          <span className="legend-color critical"></span>
          <span>CRITICAL</span>
        </div>
        <div className="legend-item">
          <span className="legend-color high"></span>
          <span>HIGH</span>
        </div>
        <div className="legend-item">
          <span className="legend-color medium"></span>
          <span>MEDIUM</span>
        </div>
        <div className="legend-item">
          <span className="legend-color low"></span>
          <span>LOW</span>
        </div>
      </div>
    </div>
  );
};
