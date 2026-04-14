import React, { useEffect, useMemo, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Html } from '@react-three/drei';
import * as THREE from 'three';
import { useStore } from '../store/useStore';
import { IntelligenceEvent } from '../types';
import { GlobeLayers } from './GlobeLayers';
import { ArcGISLayer } from './ArcGISLayer';
import { StreetViewPanel } from './StreetViewPanel';
import { WeatherControls } from './WeatherControls';
import { GeoPrecisionPanel } from './GeoPrecisionPanel';
import { CyberIntelPanel } from './CyberIntelPanel';
import { AdvancedCyberPanel } from './AdvancedCyberPanel';
import { SignalIntelPanel } from './SignalIntelPanel';
import { ThreatIntelPanel } from './ThreatIntelPanel';
import { GraphVisualization } from './GraphVisualization';
import { LiveOSINDashboard } from './LiveOSINDashboard';
import { AutonomousMonitor } from './AutonomousMonitor';
import { LearningHUD } from './LearningHUD';
import { CivilizationHUD } from './CivilizationHUD';
import { ConsciousnessHUD } from './ConsciousnessHUD';

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

const EventPoint = ({ event, position, onSelect }: { event: IntelligenceEvent; position: THREE.Vector3; onSelect: (id: string) => void }) => {
  const meshRef = React.useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = React.useState(false);
  const [clicked, setClicked] = React.useState(false);
  
  return (
    <group>
      <mesh 
        ref={meshRef} 
        position={position}
        onPointerEnter={() => setHovered(true)}
        onPointerLeave={() => setHovered(false)}
        onClick={() => {
          setClicked(!clicked);
          onSelect(event.id);
        }}
      >
        <sphereGeometry args={[clicked ? 0.04 : 0.025, 12, 12]} />
        <meshStandardMaterial 
          color={getColorByConfidence(event.severity)} 
          emissive={getColorByConfidence(event.severity)}
          emissiveIntensity={hovered || clicked ? 1.0 : 0.5}
        />
      </mesh>
      {(hovered || clicked) && (
        <Html
          position={position}
          center
          distanceFactor={10}
        >
          <div style={{
            background: 'rgba(0, 0, 0, 0.95)',
            color: '#00ff00',
            padding: '12px',
            borderRadius: '6px',
            fontSize: '12px',
            minWidth: '220px',
            border: '2px solid' + getColorByConfidence(event.severity),
            boxShadow: '0 0 15px ' + getColorByConfidence(event.severity),
            backdropFilter: 'blur(4px)',
            pointerEvents: 'none'
          }}>
            <div style={{ fontWeight: 'bold', marginBottom: '6px', borderBottom: '1px solid #333', paddingBottom: '4px', textTransform: 'uppercase' }}>
              Intelligence Signal
            </div>
            <div style={{ marginBottom: '8px', lineHeight: '1.4' }}>{event.content}</div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: '#888' }}>
              <span>Source: {event.source}</span>
              <span>Conf: {(event.confidence * 100).toFixed(1)}%</span>
            </div>
            {event.location_name && (
              <div style={{ marginTop: '4px', fontSize: '10px', color: '#00aaff' }}>
                📍 {event.location_name}
              </div>
            )}
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
};const GlobeScene = () => {
  const { events, setClusters, setHeatmap } = useStore();
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);
  const [activeWeatherLayer, setActiveWeatherLayer] = useState<string | null>(null);
  const [weatherOpacity, setWeatherOpacity] = useState(0.6);
  const [showCyberRecon, setShowCyberRecon] = useState(false);
  const [showAdvancedCyber, setShowAdvancedCyber] = useState(false);
  const [showSignalIntel, setShowSignalIntel] = useState(false);
  const [showThreatIntel, setShowThreatIntel] = useState(false);
  const [showGraphViz, setShowGraphViz] = useState(false);
  const [showLiveIntel, setShowLiveIntel] = useState(false);
  const [showAutonomous, setShowAutonomous] = useState(false);
  const [showLearning, setShowLearning] = useState(false);
  const [showCivilization, setShowCivilization] = useState(false);
  const [showConscious, setShowConscious] = useState(false);
  
  const { addEvent } = useStore(); // Assuming useStore has an addEvent action
  
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

  const selectedEvent = events.find(e => e.id === selectedEventId);
  
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
      
      {/* Global Weather Overlay */}
      {selectedEvent?.weather_intel && activeWeatherLayer && (
        <WeatherLayer 
          tileUrl={selectedEvent.weather_intel.weather_layers[activeWeatherLayer]?.tile_url} 
          opacity={weatherOpacity} 
        />
      )}

      {/* Strategic Terrain Displacement Overlay */}
      {selectedEvent?.topo_intel && terrainVisible && (
        <TerrainLayer 
          elevationData={selectedEvent.topo_intel.elevation_data} 
          opacity={terrainOpacity} 
        />
      )}

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
          onSelect={(id) => setSelectedEventId(id)}
        />
      ))}
      
      {/* ArcGIS Features Layer */}
      {selectedEvent?.arcgis_intel && (
        <ArcGISLayer event={selectedEvent} arcgisData={selectedEvent.arcgis_intel} />
      )}

      {/* NASA Worldview Satellite Layers */}
      <GlobeLayers />
      
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

      <Html fullscreen portal={document.body as HTMLElement}>
        <div style={{ pointerEvents: 'none', position: 'absolute', inset: 0 }}>
          {selectedEventId && (
            <div style={{ pointerEvents: 'auto' }}>
              <StreetViewPanel 
                eventId={selectedEventId} 
                onClose={() => setSelectedEventId(null)} 
              />
            </div>
          )}

          {selectedEvent?.weather_intel && (
            <div style={{ pointerEvents: 'auto' }}>
              <WeatherControls 
                weatherData={selectedEvent.weather_intel}
                onLayerChange={setActiveWeatherLayer}
                onOpacityChange={setWeatherOpacity}
                onClose={() => setSelectedEventId(null)}
              />
            </div>
          )}

          {selectedEvent?.topo_intel && (
            <div style={{ pointerEvents: 'auto' }}>
              <TerrainControls 
                topoData={selectedEvent.topo_intel}
                onOpacityChange={setTerrainOpacity}
                onToggleTerrain={() => setTerrainVisible(!terrainVisible)}
                onClose={() => setSelectedEventId(null)}
              />
            </div>
          )}

          {/* Photographic Intelligence Trigger */}
          <div style={{ pointerEvents: 'auto', position: 'absolute', bottom: '20px', left: '20px' }}>
            <button 
              onClick={() => setShowImageIngest(true)}
              style={{
                background: 'rgba(0, 255, 0, 0.1)',
                border: '1px solid #00ff00',
                color: '#00ff00',
                padding: '10px 20px',
                borderRadius: '4px',
                fontSize: '11px',
                textTransform: 'uppercase',
                letterSpacing: '1px',
                cursor: 'pointer',
                boxShadow: '0 0 15px rgba(0, 255, 0, 0.2)'
              }}
            >
              📷 Analyze Imagery
            </button>
            <button 
              onClick={() => setShowAudioIngest(true)}
              style={{
                background: 'rgba(0, 255, 0, 0.1)',
                border: '1px solid #00ff00',
                color: '#00ff00',
                padding: '10px 20px',
                borderRadius: '4px',
                fontSize: '11px',
                textTransform: 'uppercase',
                letterSpacing: '1px',
                marginLeft: '10px',
                cursor: 'pointer',
                boxShadow: '0 0 15px rgba(0, 255, 0, 0.2)'
              }}
            >
              🎵 AUDINT Ingest
            </button>
            <button 
              onClick={() => setShowPrecisionNav(true)}
              style={{
                background: 'rgba(0, 85, 255, 0.1)',
                border: '1px solid #0055ff',
                color: '#0055ff',
                padding: '10px 20px',
                borderRadius: '4px',
                fontSize: '11px',
                textTransform: 'uppercase',
                letterSpacing: '1px',
                marginLeft: '10px',
                cursor: 'pointer',
                boxShadow: '0 0 15px rgba(0, 85, 255, 0.2)'
              }}
            >
              🛰️ Precision Nav
            </button>
            <button 
              onClick={() => setShowCyberRecon(true)}
              style={{
                background: 'rgba(0, 119, 255, 0.1)',
                border: '1px solid #0077ff',
                color: '#0077ff',
                padding: '10px 20px',
                borderRadius: '4px',
                fontSize: '11px',
                textTransform: 'uppercase',
                letterSpacing: '1px',
                marginLeft: '10px',
                cursor: 'pointer',
                boxShadow: '0 0 15px rgba(0, 119, 255, 0.2)'
              }}
            >
              🛡️ Cyber Recon
            </button>
            <button 
              onClick={() => setShowAdvancedCyber(true)}
              style={{
                background: 'rgba(0, 255, 100, 0.1)',
                border: '1px solid #00ff66',
                color: '#00ff66',
                padding: '10px 20px',
                borderRadius: '4px',
                fontSize: '11px',
                textTransform: 'uppercase',
                letterSpacing: '1px',
                marginLeft: '10px',
                cursor: 'pointer',
                boxShadow: '0 0 15px rgba(0, 255, 100, 0.2)'
              }}
            >
              ⚡🛡️ Pro-Recon
            </button>
            <button 
              onClick={() => setShowSignalIntel(true)}
              style={{
                background: 'rgba(0, 200, 255, 0.1)',
                border: '1px solid #00c8ff',
                color: '#00c8ff',
                padding: '10px 20px',
                borderRadius: '4px',
                fontSize: '11px',
                textTransform: 'uppercase',
                letterSpacing: '1px',
                marginLeft: '10px',
                cursor: 'pointer',
                boxShadow: '0 0 15px rgba(0, 200, 255, 0.2)'
              }}
            >
              📡 Signal Intel
            </button>
            <button 
              onClick={() => setShowThreatIntel(true)}
              style={{
                background: 'rgba(255, 60, 0, 0.1)',
                border: '1px solid #ff3c00',
                color: '#ff3c00',
                padding: '10px 20px',
                borderRadius: '4px',
                fontSize: '11px',
                textTransform: 'uppercase',
                letterSpacing: '1px',
                marginLeft: '10px',
                cursor: 'pointer',
                boxShadow: '0 0 15px rgba(255, 60, 0, 0.2)'
              }}
            >
              ☣️ Threat Intel
            </button>
            <button 
              onClick={() => setShowGraphViz(true)}
              style={{
                background: 'rgba(210, 210, 210, 0.1)',
                border: '1px solid #74b9ff',
                color: '#74b9ff',
                padding: '10px 20px',
                borderRadius: '4px',
                fontSize: '11px',
                textTransform: 'uppercase',
                letterSpacing: '1px',
                marginLeft: '10px',
                cursor: 'pointer',
                boxShadow: '0 0 15px rgba(116, 185, 255, 0.2)'
              }}
            >
              🔗 Graph Reasoning
            </button>
            <button 
              onClick={() => setShowLiveIntel(true)}
              style={{
                background: 'rgba(0, 255, 150, 0.1)',
                border: '1px solid #00ff96',
                color: '#00ff96',
                padding: '10px 20px',
                borderRadius: '4px',
                fontSize: '11px',
                textTransform: 'uppercase',
                letterSpacing: '1px',
                marginLeft: '10px',
                cursor: 'pointer',
                boxShadow: '0 0 15px rgba(0, 255, 150, 0.2)'
              }}
            >
              🚀 Live Intel
            </button>
            <button 
              onClick={() => setShowAutonomous(true)}
              style={{
                background: 'rgba(210, 210, 210, 0.1)',
                border: '1px solid #00d2ff',
                color: '#00d2ff',
                padding: '10px 20px',
                borderRadius: '4px',
                fontSize: '11px',
                textTransform: 'uppercase',
                letterSpacing: '1px',
                marginLeft: '10px',
                cursor: 'pointer',
                boxShadow: '0 0 15px rgba(0, 210, 255, 0.2)'
              }}
            >
              🧠 Autonomous Core
            </button>
            <button 
              onClick={() => setShowLearning(true)}
              style={{
                background: 'rgba(150, 0, 255, 0.1)',
                border: '1px solid #bf00ff',
                color: '#bf00ff',
                padding: '10px 20px',
                borderRadius: '4px',
                fontSize: '11px',
                textTransform: 'uppercase',
                letterSpacing: '1px',
                marginLeft: '10px',
                cursor: 'pointer',
                boxShadow: '0 0 15px rgba(191, 0, 255, 0.2)'
              }}
            >
              🎓 Learning Organism
            </button>
            <button 
              onClick={() => setShowCivilization(true)}
              style={{
                background: 'rgba(0, 255, 204, 0.1)',
                border: '1px solid #00ffcc',
                color: '#00ffcc',
                padding: '10px 20px',
                borderRadius: '4px',
                fontSize: '11px',
                textTransform: 'uppercase',
                letterSpacing: '1px',
                marginLeft: '10px',
                cursor: 'pointer',
                boxShadow: '0 0 15px rgba(0, 255, 204, 0.2)'
              }}
            >
              🌍 Global Civilization
            </button>
            <button 
              onClick={() => setShowConscious(true)}
              style={{
                background: 'rgba(255, 215, 0, 0.1)',
                border: '1px solid #ffd700',
                color: '#ffd700',
                padding: '10px 20px',
                borderRadius: '4px',
                fontSize: '11px',
                textTransform: 'uppercase',
                letterSpacing: '1px',
                marginLeft: '10px',
                cursor: 'pointer',
                boxShadow: '0 0 15px rgba(255, 215, 0, 0.2)'
              }}
            >
              ✨ God Mode
            </button>
          </div>

          {showImageIngest && (
            <div style={{ pointerEvents: 'auto' }}>
              <AdvancedForensicsPanel 
                onForensicsComplete={(result) => {
                  addEvent({
                    id: result.event_id,
                    content: `DFINT Signal: [Authenticity: ${result.authenticity_score.toFixed(1)}%]`,
                    location: { lat: 0, lng: 0 },
                    source: 'forensics_pro',
                    severity: result.authenticity_score < 60 ? 'critical' : 'medium',
                    confidence: result.authenticity_score / 100,
                    timestamp: Date.now() / 1000,
                    forensics_pro: result
                  });
                }}
                onClose={() => setShowImageIngest(false)}
              />
            </div>
          )}

          {showAudioIngest && (
            <div style={{ pointerEvents: 'auto' }}>
              <AudioAnalysisPanel 
                onAudioAnalyzed={(result) => {
                  addEvent({
                    id: result.event_id,
                    content: `AUDINT Signal: ${result.scene_classification.scene_type} Environment`,
                    location: { lat: 0, lng: 0 },
                    source: 'audio_intelligence',
                    severity: 'medium',
                    confidence: result.confidence_score / 100,
                    timestamp: Date.now() / 1000,
                    audio_intel: result
                  });
                }}
                onClose={() => setShowAudioIngest(false)}
              />
            </div>
          )}

          {showPrecisionNav && (
            <div style={{ pointerEvents: 'auto' }}>
              <GeoPrecisionPanel 
                onWaypointsAnalyzed={(result) => {
                  addEvent({
                    id: result.request_id,
                    content: `PNT Signal: ${result.results.total_distance_km.toFixed(2)}km High-Precision Audit`,
                    location: { lat: 0, lng: 0 },
                    source: 'geo_precision',
                    severity: 'medium',
                    confidence: 0.95,
                    timestamp: Date.now() / 1000,
                    geo_precision: result
                  });
                }}
                onClose={() => setShowPrecisionNav(false)}
              />
            </div>
          )}

          {showCyberRecon && (
            <div style={{ pointerEvents: 'auto' }}>
              <CyberIntelPanel 
                onCyberAnalysisComplete={(result) => {
                  addEvent({
                    id: result.request_id,
                    content: `CYBINT Signal: ${result.target} [Risk: ${result.risk_assessment.risk_level}]`,
                    location: { lat: 0, lng: 0 },
                    source: 'cyber_intelligence',
                    severity: result.risk_assessment.risk_level === 'HIGH' ? 'critical' : 'medium',
                    confidence: 0.9,
                    timestamp: Date.now() / 1000,
                    cyber_intel: result
                  });
                }}
                onClose={() => setShowCyberRecon(false)}
              />
            </div>
          )}

          {showAdvancedCyber && (
            <div style={{ pointerEvents: 'auto' }}>
              <AdvancedCyberPanel 
                onAdvancedScanComplete={(result) => {
                  addEvent({
                    id: result.scan_id,
                    content: `PRO-CYBINT: ${result.target} | Risk Score: ${result.risk_assessment.risk_score}`,
                    location: { lat: 0, lng: 0 },
                    source: 'cyber_advanced',
                    severity: result.risk_assessment.risk_level === 'CRITICAL' ? 'critical' : 'high',
                    confidence: 0.95,
                    timestamp: Date.now() / 1000,
                    cyber_advanced: result
                  });
                }}
                onClose={() => setShowAdvancedCyber(false)}
              />
            </div>
          )}

          {showSignalIntel && (
            <div style={{ pointerEvents: 'auto' }}>
              <SignalIntelPanel 
                onSignalScanComplete={(result) => {
                  addEvent({
                    id: result.request_id,
                    content: `SIGINT Signal: ${result.target} | ${result.email_intel.emails?.length || 0} exposed assets`,
                    location: { lat: 0, lng: 0 },
                    source: 'signal_intelligence',
                    severity: result.risk_assessment.risk_level === 'HIGH' ? 'critical' : 'medium',
                    confidence: 0.92,
                    timestamp: Date.now() / 1000,
                    signal_intel: result
                  });
                }}
                onClose={() => setShowSignalIntel(false)}
              />
            </div>
          )}

          {showThreatIntel && (
            <div style={{ pointerEvents: 'auto' }}>
              <ThreatIntelPanel 
                onThreatAssessmentComplete={(result) => {
                  const eventId = result.target + Date.now();
                  addEvent({
                    id: eventId,
                    content: `CTI Signal: ${result.target} | Threat Intensity: ${result.threat_score}`,
                    location: { lat: 0, lng: 0 },
                    source: 'threat_intelligence',
                    severity: result.threat_level === 'high' ? 'critical' : 'medium',
                    confidence: 0.95,
                    timestamp: Date.now() / 1000,
                    threat_intel: result
                  });
                  
                  // Cross-reference with Graph Core
                  fetch('http://localhost:8020/entities', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                      type: 'threat_signal',
                      properties: { target: result.target, score: result.threat_score },
                      source_modules: ['threat_intel']
                    })
                  });
                }}
                onClose={() => setShowThreatIntel(false)}
              />
            </div>
          )}

          {showGraphViz && (
            <div style={{ pointerEvents: 'auto' }}>
              <GraphVisualization 
                onClose={() => setShowGraphViz(false)}
              />
            </div>
          )}

          {showLiveIntel && (
            <div style={{ pointerEvents: 'auto' }}>
              <LiveOSINDashboard 
                onClose={() => setShowLiveIntel(false)}
              />
            </div>
          )}

          {showAutonomous && (
            <div style={{ pointerEvents: 'auto' }}>
              <AutonomousMonitor 
                onClose={() => setShowAutonomous(false)}
              />
            </div>
          )}

          {showLearning && (
            <div style={{ pointerEvents: 'auto' }}>
              <LearningHUD 
                onClose={() => setShowLearning(false)}
              />
            </div>
          )}

          {showCivilization && (
            <div style={{ pointerEvents: 'auto' }}>
              <CivilizationHUD 
                onClose={() => setShowCivilization(false)}
              />
            </div>
          )}

          {showConscious && (
            <div style={{ pointerEvents: 'auto' }}>
              <ConsciousnessHUD 
                onClose={() => setShowConscious(false)}
              />
            </div>
          )}
        </div>
      </Html>
    </>
  );
};
;

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
