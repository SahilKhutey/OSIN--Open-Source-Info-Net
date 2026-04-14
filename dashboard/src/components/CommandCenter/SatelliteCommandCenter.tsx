import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import * as THREE from 'three';
import { Activity, Shield, Cpu, Target, Radar, Terminal as TerminalIcon, Maximize2 } from 'lucide-react';
import './SatelliteCommandCenter.css';

interface Alert {
  id: string;
  level: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  msg: string;
  lat: number;
  lon: number;
  timestamp: Date;
  source: string;
  confidence: number;
  type: string;
}

const SatelliteCommandCenter: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [systemStatus] = useState({
    ingestion: 'ACTIVE',
    graphCore: 'ONLINE',
    aiReasoning: 'STABLE',
    threatLevel: 'ELEVATED',
    satelliteOverlay: 'ACTIVE'
  });
  
  const globeRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene>();
  const rendererRef = useRef<THREE.WebGLRenderer>();
  const cameraRef = useRef<THREE.PerspectiveCamera>();
  const earthRef = useRef<THREE.Mesh>();

  // Initialize Three.js scene
  useEffect(() => {
    if (!globeRef.current) return;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(
      75,
      globeRef.current.clientWidth / globeRef.current.clientHeight,
      0.1,
      1000
    );
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });

    renderer.setSize(globeRef.current.clientWidth, globeRef.current.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    globeRef.current.appendChild(renderer.domElement);

    // Create Earth with Satellite Texture
    const geometry = new THREE.SphereGeometry(5, 64, 64);
    const textureLoader = new THREE.TextureLoader();
    
    // High-Res Satellite Earth Texture from CDN
    const earthTexture = textureLoader.load('https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg');

    const material = new THREE.MeshPhongMaterial({
      map: earthTexture,
      specular: new THREE.Color(0x333333),
      shininess: 5
    });

    const earth = new THREE.Mesh(geometry, material);
    scene.add(earth);

    // Add atmospheric glow
    const glowGeometry = new THREE.SphereGeometry(5.15, 64, 64);
    const glowMaterial = new THREE.MeshBasicMaterial({
      color: 0x0077ff,
      transparent: true,
      opacity: 0.1,
      side: THREE.BackSide
    });
    const atmosphere = new THREE.Mesh(glowGeometry, glowMaterial);
    scene.add(atmosphere);

    // Add lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
    directionalLight.position.set(5, 3, 5);
    scene.add(directionalLight);

    camera.position.z = 12;

    sceneRef.current = scene;
    rendererRef.current = renderer;
    cameraRef.current = camera;
    earthRef.current = earth;

    const animate = () => {
      requestAnimationFrame(animate);
      if (earthRef.current) earthRef.current.rotation.y += 0.001;
      renderer.render(scene, camera);
    };
    animate();

    const handleResize = () => {
      if (camera && renderer && globeRef.current) {
        camera.aspect = globeRef.current.clientWidth / globeRef.current.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(globeRef.current.clientWidth, globeRef.current.clientHeight);
      }
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (globeRef.current && renderer.domElement) {
        globeRef.current.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, []);

  // Simulate real-time alerts
  useEffect(() => {
    const alertInterval = setInterval(() => {
      const newAlert: Alert = {
        id: `sat-${Date.now()}`,
        level: ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'][Math.floor(Math.random() * 4)] as any,
        msg: generateAlertMessage(),
        lat: Math.random() * 180 - 90,
        lon: Math.random() * 360 - 180,
        timestamp: new Date(),
        source: ['SATELLITE-X', 'GEOINT-4', 'THERMAL-EYE'][Math.floor(Math.random() * 3)],
        confidence: Math.random() * 0.3 + 0.7,
        type: 'geospatial_anomaly'
      };
      setAlerts(prev => [newAlert, ...prev].slice(0, 20));
      addMarker(newAlert);
    }, 4000);

    return () => clearInterval(alertInterval);
  }, []);

  const addMarker = (alert: Alert) => {
    if (!sceneRef.current) return;
    const markerGeo = new THREE.SphereGeometry(0.12, 16, 16);
    const color = alert.level === 'CRITICAL' ? 0xff0000 : alert.level === 'HIGH' ? 0xffaa00 : 0x00ffcc;
    const markerMat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.9 });
    const marker = new THREE.Mesh(markerGeo, markerMat);

    const phi = (90 - alert.lat) * Math.PI / 180;
    const theta = (alert.lon + 180) * Math.PI / 180;
    const r = 5.05;
    marker.position.set(
      -r * Math.sin(phi) * Math.cos(theta),
      r * Math.cos(phi),
      r * Math.sin(phi) * Math.sin(theta)
    );
    sceneRef.current.add(marker);
    
    // Auto-cleanup marker
    setTimeout(() => {
      if (sceneRef.current) sceneRef.current.remove(marker);
      markerGeo.dispose();
      markerMat.dispose();
    }, 15000);
  };

  const generateAlertMessage = () => {
    const msgs = ['Thermal Anomaly Detected', 'Moving Carrier Strike Group', 'Facility Expansion Observed', 'Signal Intercept Match', 'Optical Occlusion Pattern'];
    return msgs[Math.floor(Math.random() * msgs.length)];
  };

  const triggerIngest = async (alert: Alert) => {
    try {
      await fetch('http://localhost:8020/ingest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id: alert.id,
          text: alert.msg,
          lat: alert.lat,
          lon: alert.lon,
          type: alert.level,
          source: alert.source,
          confidence: alert.confidence
        })
      });
      console.log(`Ingested: ${alert.id}`);
    } catch (e) {
      console.error('Ingest failed:', e);
    }
  };

  return (
    <div className="sat-center">
      <header className="sat-header">
        <div className="branding">
          <Radar className="sat-logo" />
          <div className="title">
            <h1>OSIN Satellite Intelligence</h1>
            <span>High-Altitude Surveillance Layer // System 8.0.0</span>
          </div>
        </div>
        <div className="threat-level">
          <span className="label">Threat Level:</span>
          <span className="val">ELEVATED</span>
        </div>
      </header>

      <main className="sat-content">
        {/* Left: System Nodes */}
        <section className="col-nodes">
          <div className="panel-title">Infrastructure Meta-Node</div>
          <div className="status-grid">
            {Object.entries(systemStatus).map(([k, v]) => (
              <div className="status-item" key={k}>
                <span className="k">{k.replace(/([A-Z])/g, ' $1')}</span>
                <span className={`v ${v === 'ACTIVE' || v === 'ONLINE' ? 'green' : 'amber'}`}>{v}</span>
              </div>
            ))}
          </div>
          <div className="risk-meter">
             <div className="meter-label">Global Risk Index: 67%</div>
             <div className="meter-track"><div className="meter-fill" style={{ width: '67%' }} /></div>
          </div>
        </section>

        {/* Center: Satellite Globe */}
        <section className="col-globe">
           <div className="globe-controls">
             <button className="ctrl-btn">HEATMAP</button>
             <button className="ctrl-btn active">SATELLITE</button>
             <button className="ctrl-btn">THERMAL</button>
           </div>
           <div ref={globeRef} className="globe-viewport" />
           <div className="alert-marquee">
              {alerts.slice(0, 3).map(a => (
                <div className="marquee-item" key={a.id} onClick={() => triggerIngest(a)}>
                  <span className={`prio ${a.level}`}>{a.level}</span>
                  <span className="msg">{a.msg}</span>
                  <span className="coord">{a.lat.toFixed(2)}, {a.lon.toFixed(2)}</span>
                </div>
              ))}
           </div>
        </section>

        {/* Right: Live Telemetry */}
        <section className="col-telemetry">
           <div className="panel-title">Imagery Feed // Telemetry</div>
           <div className="telemetry-list">
              {alerts.map(a => (
                <div className="tele-item" key={a.id}>
                  <div className="t-head">
                    <span className="time">{a.timestamp.toLocaleTimeString()}</span>
                    <span className="source">{a.source}</span>
                  </div>
                  <div className="t-body">{a.msg}</div>
                  <div className="t-foot">Confidence: {Math.round(a.confidence*100)}%</div>
                </div>
              ))}
           </div>
        </section>
      </main>

      <footer className="sat-footer">
        <div className="f-left"><TerminalIcon size={12} /> <span>&gt; satellite telemetry streaming at 4.2 Tbit/s</span></div>
        <div className="f-right">OSIN Project // Level 15 Mastership</div>
      </footer>
    </div>
  );
};

export default SatelliteCommandCenter;
