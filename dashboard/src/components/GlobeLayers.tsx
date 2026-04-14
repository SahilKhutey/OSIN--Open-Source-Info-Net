import React, { useEffect, useMemo, useRef } from 'react';
import { useFrame, useLoader } from '@react-three/fiber';
import * as THREE from 'three';
import { useStore } from '../store/useStore';

// Helper to convert lat/lon to Vector3
const latLonToVector3 = (lat: number, lng: number, radius: number = 1.05) => {
  const phi = (90 - lat) * (Math.PI / 180);
  const theta = (lng + 180) * (Math.PI / 180);
  
  return new THREE.Vector3(
    -radius * Math.sin(phi) * Math.cos(theta),
    radius * Math.cos(phi),
    radius * Math.sin(phi) * Math.sin(theta)
  );
};

const getColorForConfidence = (confidence: number) => {
  if (confidence >= 0.8) return new THREE.Color(0xff0000); // Red - High
  if (confidence >= 0.5) return new THREE.Color(0xff9900); // Orange - Medium
  return new THREE.Color(0x00ff00); // Green - Low
};

interface NASALayerProps {
  layerName: string;
  tileUrl: string;
  lat: number;
  lon: number;
  eventId: string;
  confidence: number;
  timestamp: string;
}

const NASALayerTile: React.FC<NASALayerProps> = ({ layerName, tileUrl, lat, lon, eventId, confidence, timestamp }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  
  // Parse GIBS URL template (Level 9 by default)
  // Example: ...Level9/{z}/{y}/{x}.jpg
  const formattedUrl = useMemo(() => {
    return tileUrl.replace('{z}', '9').replace('{y}', '100').replace('{x}', '100');
  }, [tileUrl]);

  const texture = useLoader(THREE.TextureLoader, formattedUrl);
  const position = useMemo(() => latLonToVector3(lat, lon, 1.02), [lat, lon]);
  const markerPosition = useMemo(() => latLonToVector3(lat, lon, 1.05), [lat, lon]);

  return (
    <group>
      {/* Event Satellite Layer Texture */}
      <mesh position={position} lookAt={new THREE.Vector3(0, 0, 0)}>
        <planeGeometry args={[0.25, 0.25]} />
        <meshBasicMaterial 
          map={texture} 
          transparent 
          opacity={0.8} 
          blending={THREE.AdditiveBlending}
          side={THREE.DoubleSide}
        />
      </mesh>

      {/* Confidence-Colored Performance Marker */}
      <mesh position={markerPosition}>
        <sphereGeometry args={[0.015, 12, 12]} />
        <meshBasicMaterial 
          color={getColorForConfidence(confidence)}
          transparent
          opacity={0.9}
        />
      </mesh>
    </group>
  );
};

export const GlobeLayers: React.FC = () => {
  const { events } = useStore();
  const layersRef = useRef<Map<string, number>>(new Map()); // id -> addedTime
  
  // Filter enriched events
  const enrichedEvents = useMemo(() => {
    return events.filter(e => e.geo_intel && e.geo_intel.tile_urls);
  }, [events]);

  // Automatic Lifecycle Management: Cleanup old layers from memory state if needed
  // In a React-Three-Fiber component, we handle this by filtering 'events' 
  // but we can add a visual timeout if we had local state.
  
  return (
    <group>
      {enrichedEvents.map(event => {
        const { lat, lon } = event.location || { lat: 0, lon: 0 };
        return Object.entries(event.geo_intel.tile_urls).map(([layerName, url]) => (
          <NASALayerTile
            key={`${event.id}-${layerName}`}
            eventId={event.id}
            layerName={layerName}
            tileUrl={url as string}
            lat={lat}
            lon={lon}
            confidence={event.confidence || 0.5}
            timestamp={event.geo_intel.timestamp}
          />
        ));
      })}
    </group>
  );
};

export default GlobeLayers;
