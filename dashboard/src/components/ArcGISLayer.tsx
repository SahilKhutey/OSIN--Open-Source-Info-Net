import React, { useMemo } from 'react';
import * as THREE from 'three';

interface ArcGISFeature {
  attributes: Record<string, any>;
  geometry: { x: number; y: number };
  service: string;
  distance_km: number;
}

interface ArcGISLayerProps {
  event: { lat: number; lon: number; id: string };
  arcgisData: {
    features: Record<string, ArcGISFeature[]>;
  };
}

const SERVICE_COLORS: Record<string, string> = {
  earthquakes: '#ff0000',
  wildfires: '#ff5500',
  infrastructure: '#00ff00',
  transportation: '#0000ff',
  weather_alerts: '#ffff00',
  default: '#ffffff'
};

const latLonToVector3 = (lat: number, lng: number, radius: number = 1.0) => {
  const phi = (90 - lat) * (Math.PI / 180);
  const theta = (lng + 180) * (Math.PI / 180);
  
  return new THREE.Vector3(
    -radius * Math.sin(phi) * Math.cos(theta),
    radius * Math.cos(phi),
    radius * Math.sin(phi) * Math.sin(theta)
  );
};

export const ArcGISLayer: React.FC<ArcGISLayerProps> = ({ event, arcgisData }) => {
  const eventPos = useMemo(() => latLonToVector3(event.lat, event.lon, 1.01), [event]);

  const featureGeometries = useMemo(() => {
    const markers: { position: THREE.Vector3; color: string; info: any }[] = [];
    const lines: { points: THREE.Vector3[]; color: string }[] = [];

    Object.entries(arcgisData.features).forEach(([serviceKey, features]) => {
      const color = SERVICE_COLORS[serviceKey] || SERVICE_COLORS.default;
      
      features.forEach((feature, idx) => {
        const featLat = feature.geometry?.y;
        const featLon = feature.geometry?.x;
        
        if (featLat !== undefined && featLon !== undefined) {
          const featPos = latLonToVector3(featLat, featLon, 1.02);
          
          markers.push({ 
            position: featPos, 
            color,
            info: { ...feature.attributes, service: serviceKey }
          });

          // Connection line from event to feature
          lines.push({
            points: [eventPos, featPos],
            color
          });
        }
      });
    });

    return { markers, lines };
  }, [eventPos, arcgisData]);

  return (
    <group>
      {/* GIS Feature Markers */}
      {featureGeometries.markers.map((marker, idx) => (
        <mesh key={`marker-${idx}`} position={marker.position}>
          <sphereGeometry args={[0.012, 12, 12]} />
          <meshBasicMaterial color={marker.color} transparent opacity={0.6} />
        </mesh>
      ))}

      {/* Verification Vectors */}
      {featureGeometries.lines.map((line, idx) => (
        <line key={`line-${idx}`}>
          <bufferGeometry attach="geometry">
            <float32BufferAttribute
              attach="attributes-position"
              args={[new Float32Array([...line.points[0].toArray(), ...line.points[1].toArray()]), 3]}
            />
          </bufferGeometry>
          <lineBasicMaterial attach="material" color={line.color} transparent opacity={0.3} linewidth={1} />
        </line>
      ))}
    </group>
  );
};

export default ArcGISLayer;
