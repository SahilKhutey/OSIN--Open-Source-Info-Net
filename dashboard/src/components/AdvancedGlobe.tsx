import React, { useEffect, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Html } from '@react-three/drei';
import * as THREE from 'three';
import { useStore } from '../store/useStore';
import { IntelligenceEvent } from '../types';

const clusterEvents = (events: IntelligenceEvent[], radius: number = 2.0, minPoints: number = 2) => {
  const clusters: any[] = [];
  const visited = new Set<string>();
  
  events.forEach(event => {
    if (!event.location || visited.has(event.id)) return;
    
    const neighbors = events.filter(e => 
      e.location && 
      e.id !== event.id && 
      calculateDistance(event.location!, e.location!) < radius
    );
    
    if (neighbors.length >= minPoints) {
      const cluster = [event, ...neighbors];
      clusters.push({
        center: calculateClusterCenter(cluster),
        events: cluster,
        intensity: cluster.length
      });
      
      cluster.forEach(e => visited.add(e.id));
    }
  });
  
  return clusters;
};

const calculateDistance = (loc1: { lat: number; lng: number }, loc2: { lat: number; lng: number }) => {
  const R = 6371;
  const dLat = (loc2.lat - loc1.lat) * Math.PI / 180;
  const dLon = (loc2.lng - loc1.lng) * Math.PI / 180;
  const a = 
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(loc1.lat * Math.PI / 180) * Math.cos(loc2.lat * Math.PI / 180) * 
    Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
};

const calculateClusterCenter = (events: IntelligenceEvent[]) => {
  const latSum = events.reduce((sum, e) => sum + (e.location?.lat || 0), 0);
  const lngSum = events.reduce((sum, e) => sum + (e.location?.lng || 0), 0);
  return {
    lat: latSum / events.length,
    lng: lngSum / events.length
  };
};

const latLonToVector3 = (lat: number, lng: number, radius: number = 1) => {
  const phi = (90 - lat) * (Math.PI / 180);
  const theta = (lng + 180) * (Math.PI / 180);
  
  return new THREE.Vector3(
    -radius * Math.sin(phi) * Math.cos(theta),
    radius * Math.cos(phi),
    radius * Math.sin(phi) * Math.sin(theta)
  );
};

const generateHeatmap = (clusters: any[]) => {
  return clusters.map(cluster => {
    const position = latLonToVector3(cluster.center.lat, cluster.center.lng);
    return {
      position,
      intensity: Math.min(1, cluster.intensity / 10),
      events: cluster.events
    };
  });
};

const HeatmapBlob = ({ position, intensity }: { position: THREE.Vector3; intensity: number }) => {
  const meshRef = React.useRef<THREE.Mesh>(null);
  
  useFrame(() => {
    if (meshRef.current) {
      meshRef.current.scale.x = 0.5 + Math.sin(Date.now() * 0.001) * 0.1 * intensity;
      meshRef.current.scale.y = 0.5 + Math.sin(Date.now() * 0.001) * 0.1 * intensity;
      meshRef.current.scale.z = 0.5 + Math.sin(Date.now() * 0.001) * 0.1 * intensity;
    }
  });
  
  return (
    <mesh ref={meshRef} position={position}>
      <sphereGeometry args={[0.1 + intensity * 0.2, 16, 16]} />
      <meshStandardMaterial 
        color="#ff5500" 
        transparent 
        opacity={0.3 * intensity} 
        emissive="#ff5500"
        emissiveIntensity={intensity * 0.5}
      />
    </mesh>
  );
};

const EventPoint = ({ event, position }: { event: IntelligenceEvent; position: THREE.Vector3 }) => {
  const meshRef = React.useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = React.useState(false);
  
  return (
    <group>
      <mesh 
        ref={meshRef} 
        position={position}
        onPointerEnter={() => setHovered(true)}
        onPointerLeave={() => setHovered(false)}
      >
        <sphereGeometry args={[0.02, 8, 8]} />
        <meshStandardMaterial 
          color={getColorByConfidence(event.severity)} 
          emissive={getColorByConfidence(event.severity)}
          emissiveIntensity={0.5}
        />
      </mesh>
      {hovered && (
        <Html
          position={position}
          center
          distanceFactor={10}
        >
          <div style={{
            background: 'rgba(0, 0, 0, 0.9)',
            color: '#00ff00',
            padding: '8px',
            borderRadius: '4px',
            fontSize: '12px',
            maxWidth: '200px',
            border: '1px solid #00ff00'
          }}>
            <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>Event</div>
            <div>{event.content.substring(0, 50)}...</div>
          </div>
        </Html>
      )}
    </group>
  );
};

const ClusterPoint = ({ cluster, position }: { cluster: any; position: THREE.Vector3 }) => {
  const [hovered, setHovered] = React.useState(false);
  
  return (
    <group>
      <mesh 
        position={position}
        onPointerEnter={() => setHovered(true)}
        onPointerLeave={() => setHovered(false)}
      >
        <sphereGeometry args={[0.05 + cluster.intensity * 0.01, 12, 12]} />
        <meshStandardMaterial 
          color="#00ff00" 
          transparent 
          opacity={0.7} 
          emissive="#00ff00"
          emissiveIntensity={0.3}
        />
      </mesh>
      {hovered && (
        <Html position={position} center distanceFactor={15}>
          <div style={{
            background: 'rgba(0, 0, 0, 0.9)',
            color: '#00ff00',
            padding: '8px',
            borderRadius: '4px',
            fontSize: '12px',
            border: '1px solid #00ff00'
          }}>
            <div style={{ fontWeight: 'bold' }}>Cluster</div>
            <div>{cluster.events.length} events</div>
          </div>
        </Html>
      )}
    </group>
  );
};

const getColorByConfidence = (severity: string): string => {
  switch(severity) {
    case 'critical': return '#ff0000';
    case 'high': return '#ff5500';
    case 'medium': return '#ffff00';
    case 'low': return '#00ff00';
    default: return '#0088ff';
  }
};

const GlobeScene = () => {
  const { events, setClusters, setHeatmap } = useStore();
  
  useEffect(() => {
    if (events.length > 0) {
      const clusters = clusterEvents(events);
      setClusters(clusters);
      setHeatmap(generateHeatmap(clusters));
    }
  }, [events, setClusters, setHeatmap]);
  
  const { eventPoints, clusterPoints, heatmapPoints } = useMemo(() => {
    const eventPoints = events
      .filter(e => e.location)
      .map(event => ({
        event,
        position: latLonToVector3(event.location!.lat, event.location!.lng)
      }));
    
    const clusters = clusterEvents(events);
    const clusterPoints = clusters.map(cluster => ({
      cluster,
      position: latLonToVector3(cluster.center.lat, cluster.center.lng)
    }));
    
    const heatmapPoints = generateHeatmap(clusters);
    
    return { eventPoints, clusterPoints, heatmapPoints };
  }, [events]);
  
  return (
    <>
      <mesh>
        <sphereGeometry args={[1, 64, 64]} />
        <meshStandardMaterial 
          color="#1a1a2e" 
          roughness={0.8}
          metalness={0.2}
        />
      </mesh>
      
      <mesh>
        <sphereGeometry args={[1.02, 64, 64]} />
        <meshStandardMaterial 
          color="#00aaff" 
          transparent 
          opacity={0.1}
        />
      </mesh>
      
      {heatmapPoints.map((h, i) => (
        <HeatmapBlob 
          key={`heatmap-${i}`} 
          position={h.position} 
          intensity={h.intensity} 
        />
      ))}
      
      {clusterPoints.map((c, i) => (
        <ClusterPoint 
          key={`cluster-${i}`} 
          cluster={c.cluster} 
          position={c.position} 
        />
      ))}
      
      {eventPoints.map((e, i) => (
        <EventPoint 
          key={`event-${e.event.id}`} 
          event={e.event} 
          position={e.position} 
        />
      ))}
      
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} intensity={1} />
      <pointLight position={[-10, -10, -10]} intensity={0.5} color="#00aaff" />
      
      <OrbitControls 
        enableZoom={true}
        enablePan={false}
        autoRotate={true}
        autoRotateSpeed={0.5}
        minDistance={1.5}
        maxDistance={5}
      />
    </>
  );
};

export const AdvancedGlobe: React.FC = () => {
  return (
    <div style={{
      position: 'relative',
      width: '100%',
      height: '600px',
      background: '#000',
      borderRadius: '0.5rem',
      overflow: 'hidden',
      border: '1px solid #00ff00'
    }}>
      <Canvas camera={{ position: [0, 0, 2.5], fov: 60 }}>
        <GlobeScene />
      </Canvas>
      
      <div style={{
        position: 'absolute',
        bottom: '16px',
        left: '16px',
        background: 'rgba(0, 0, 0, 0.75)',
        color: '#00ff00',
        padding: '12px',
        borderRadius: '4px',
        fontSize: '14px'
      }}>
        <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>Legend</div>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
          <div style={{ width: '12px', height: '12px', background: '#ff0000', borderRadius: '50%', marginRight: '8px' }}></div>
          <span>Critical Events</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
          <div style={{ width: '12px', height: '12px', background: '#00ff00', borderRadius: '50%', marginRight: '8px' }}></div>
          <span>Clusters</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <div style={{ width: '12px', height: '12px', background: '#ff5500', borderRadius: '50%', marginRight: '8px' }}></div>
          <span>Hotspots</span>
        </div>
      </div>
    </div>
  );
};
