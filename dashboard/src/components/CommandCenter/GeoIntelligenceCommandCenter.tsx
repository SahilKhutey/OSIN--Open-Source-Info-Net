import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import * as THREE from 'three';
import { Shield, Zap, Globe, Activity, Terminal as TerminalIcon, Mic, Share2, Target } from 'lucide-react';
import { Alert, GraphConnection, SystemStatus } from '../../types/command_center';
import './GeoIntelligenceCommandCenter.css';

const GeoIntelligenceCommandCenter: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [graphConnections, setGraphConnections] = useState<GraphConnection[]>([]);
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({
    ingestion: 'ACTIVE',
    graphCore: 'ONLINE',
    aiReasoning: 'STABLE',
    threatLevel: 'ELEVATED',
    globalRisk: 42,
    voiceAnalyst: 'ONLINE'
  });

  const globeRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene>();
  const rendererRef = useRef<THREE.WebGLRenderer>();
  const cameraRef = useRef<THREE.PerspectiveCamera>();
  const earthRef = useRef<THREE.Mesh>();
  const markersRef = useRef<THREE.Mesh[]>([]);
  const connectionsRef = useRef<THREE.Line[]>([]);

  // Initialize Three.js scene with Earth
  useEffect(() => {
    if (!globeRef.current) return;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, globeRef.current.clientWidth / globeRef.current.clientHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });

    renderer.setSize(globeRef.current.clientWidth, globeRef.current.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    globeRef.current.appendChild(renderer.domElement);

    // Create Earth - Tactical Map
    const geometry = new THREE.SphereGeometry(5, 64, 64);
    const textureLoader = new THREE.TextureLoader();
    const earthTexture = textureLoader.load('https://unpkg.com/three-globe/example/img/earth-night.jpg');
    
    const material = new THREE.MeshPhongMaterial({
      map: earthTexture,
      specular: new THREE.Color(0x333333),
      shininess: 5,
      transparent: true,
      opacity: 0.8
    });

    const earth = new THREE.Mesh(geometry, material);
    scene.add(earth);

    // Atmospheric Glow
    const glowGeometry = new THREE.SphereGeometry(5.1, 64, 64);
    const glowMaterial = new THREE.MeshBasicMaterial({ color: 0x00ffcc, transparent: true, opacity: 0.1, side: THREE.BackSide });
    const atmosphere = new THREE.Mesh(glowGeometry, glowMaterial);
    scene.add(atmosphere);

    // Lighting
    scene.add(new THREE.AmbientLight(0xffffff, 0.4));
    const dirLight = new THREE.DirectionalLight(0x00ffcc, 1);
    dirLight.position.set(5, 3, 5);
    scene.add(dirLight);

    camera.position.z = 13;

    sceneRef.current = scene;
    rendererRef.current = renderer;
    cameraRef.current = camera;
    earthRef.current = earth;

    const animate = () => {
      requestAnimationFrame(animate);
      if (earthRef.current) earthRef.current.rotation.y += 0.001;
      
      // Pulse Markers
      markersRef.current.forEach((marker, index) => {
        const pulse = 1 + Math.sin(Date.now() * 0.003 + index) * 0.15;
        marker.scale.set(pulse, pulse, pulse);
      });

      renderer.render(scene, camera);
    };
    animate();

    const handleResize = () => {
      if (!globeRef.current) return;
      camera.aspect = globeRef.current.clientWidth / globeRef.current.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(globeRef.current.clientWidth, globeRef.current.clientHeight);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (globeRef.current && renderer.domElement) globeRef.current.removeChild(renderer.domElement);
      renderer.dispose();
    };
  }, []);

  // Intelligence Generation Loop
  useEffect(() => {
    const interval = setInterval(() => {
      const newAlert: Alert = {
        id: `geo-${Date.now()}`,
        level: ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'][Math.floor(Math.random() * 4)] as any,
        message: generateTacticalMessage(),
        lat: Math.random() * 160 - 80,
        lon: Math.random() * 320 - 160,
        timestamp: new Date(),
        source: ['GEOINT', 'SIGINT', 'HUMINT'][Math.floor(Math.random() * 3)],
        confidence: Math.random() * 0.4 + 0.6
      };

      setAlerts(prev => [newAlert, ...prev].slice(0, 20));
      addPin(newAlert);
      
      // Correlation logic
      if (alerts.length > 0 && Math.random() > 0.6) {
        const target = alerts[Math.floor(Math.random() * alerts.length)];
        const conn: GraphConnection = { id: `conn-${Date.now()}`, from: newAlert.id, to: target.id, strength: Math.random(), type: 'correlation' };
        setGraphConnections(prev => [conn, ...prev].slice(0, 10));
        addLink(newAlert, target);
      }
    }, 4000);

    return () => clearInterval(interval);
  }, [alerts]);

  const generateTacticalMessage = () => {
    const msgs = ['Signal Density Anomaly', 'Unauthorized Boundary Crossing', 'Data Hub Oscillation', 'Vulnerability Probe', 'Asset Proximity Alert'];
    return msgs[Math.floor(Math.random() * msgs.length)];
  };

  const addPin = (alert: Alert) => {
    if (!sceneRef.current) return;
    const markerGeo = new THREE.SphereGeometry(0.15, 16, 16);
    const color = alert.level === 'CRITICAL' ? 0xff0044 : alert.level === 'HIGH' ? 0xff8800 : 0x00ffcc;
    const markerMat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.9 });
    const marker = new THREE.Mesh(markerGeo, markerMat);

    const phi = (90 - alert.lat) * Math.PI / 180;
    const theta = (alert.lon + 180) * Math.PI / 180;
    const r = 5.02;
    marker.position.set(-r * Math.sin(phi) * Math.cos(theta), r * Math.cos(phi), r * Math.sin(phi) * Math.sin(theta));
    sceneRef.current.add(marker);
    markersRef.current.push(marker);

    setTimeout(() => {
      if (sceneRef.current) sceneRef.current.remove(marker);
      markersRef.current = markersRef.current.filter(m => m !== marker);
      markerGeo.dispose();
      markerMat.dispose();
    }, 25000);
  };

  const addLink = (from: Alert, to: Alert) => {
    if (!sceneRef.current) return;
    const r = 5.03;
    const getPos = (lat: number, lon: number) => {
        const phi = (90 - lat) * Math.PI / 180;
        const theta = (lon + 180) * Math.PI / 180;
        return new THREE.Vector3(-r * Math.sin(phi) * Math.cos(theta), r * Math.cos(phi), r * Math.sin(phi) * Math.sin(theta));
    };

    const start = getPos(from.lat, from.lon);
    const end = getPos(to.lat, to.lon);
    
    const geometry = new THREE.BufferGeometry().setFromPoints([start, end]);
    const material = new THREE.LineBasicMaterial({ color: 0x00ffcc, transparent: true, opacity: 0.4 });
    const line = new THREE.Line(geometry, material);
    sceneRef.current.add(line);
    connectionsRef.current.push(line);

    setTimeout(() => {
      if (sceneRef.current) sceneRef.current.remove(line);
      connectionsRef.current = connectionsRef.current.filter(l => l !== line);
      geometry.dispose();
      material.dispose();
    }, 15000);
  };

  const speakBriefing = () => {
    const msg = `Strategic analysis complete. Active tactical pins: ${alerts.length}. Causal correlations: ${graphConnections.length}. Dominant risk vector: ${systemStatus.threatLevel}. Systems stable in sector ${Math.floor(Math.random()*900)}.`;
    if ('speechSynthesis' in window) {
      const u = new SpeechSynthesisUtterance(msg);
      u.rate = 1.0; u.pitch = 0.8;
      speechSynthesis.speak(u);
      setSystemStatus(prev => ({ ...prev, voiceAnalyst: 'SPEAKING', aiReasoning: 'ANALYZING' }));
      setTimeout(() => setSystemStatus(prev => ({ ...prev, voiceAnalyst: 'ONLINE', aiReasoning: 'STABLE' })), 4000);
    }
  };

  return (
    <div className="geo-intel-center">
      <header className="geo-header">
        <div className="geo-branding">
          <Target className="geo-icon" />
          <div className="geo-title">
            <h1>Tactical Geo-Intelligence</h1>
            <span>Event Pin Mapping + Voice Analyst // v8.0.0</span>
          </div>
        </div>
        <div className="geo-stats">
          <div className="stat-box">
             <span className="l">Active Pins</span>
             <span className="v text-cyan-400">{alerts.length}</span>
          </div>
          <div className="stat-box">
             <span className="l">Correlations</span>
             <span className="v text-cyan-400">{graphConnections.length}</span>
          </div>
        </div>
      </header>

      <main className="geo-main">
        {/* Left: Tactical Meta */}
        <section className="geo-col-meta">
          <div className="geo-panel-label">Operational Posture</div>
          <div className="geo-status-list">
             <div className="g-item"><span>Ingestion</span> <span className="s green">ACTIVE</span></div>
             <div className="g-item"><span>Graph Core</span> <span className="s green">ONLINE</span></div>
             <div className="g-item"><span>Voice Analyst</span> <span className={`s ${systemStatus.voiceAnalyst === 'SPEAKING' ? 'pulse' : 'green'}`}>{systemStatus.voiceAnalyst}</span></div>
          </div>
          
          <div className="geo-analysis-trigger">
             <button className="briefing-btn" onClick={speakBriefing}>
                <Mic size={14} />
                <span>Audio Tactical Briefing</span>
             </button>
             <p className="hint">Click for meta-cognitive audio summary</p>
          </div>

          <div className="geo-risk-box">
             <div className="r-head">Tactical Risk Index: {Math.min(99, alerts.length * 6)}%</div>
             <div className="r-track"><div className="r-fill" style={{ width: `${Math.min(100, alerts.length * 6)}%` }} /></div>
          </div>
        </section>

        {/* Center: Intelligence Globe */}
        <section className="geo-col-globe">
           <div className="geo-globe-overlay">
              <div className="geo-legend">
                 <div className="leg"><span className="dot red" /> CRITICAL</div>
                 <div className="leg"><span className="dot amber" /> HIGH</div>
                 <div className="leg"><span className="dot cyan" /> NOMINAL</div>
              </div>
           </div>
           <div ref={globeRef} className="geo-viewport" />
        </section>

        {/* Right: Event Feed */}
        <section className="geo-col-feed">
           <div className="geo-panel-label">Tactical Intelligence Stream</div>
           <div className="geo-feed-list">
              <AnimatePresence>
                {alerts.map(a => (
                  <motion.div 
                    key={a.id} 
                    initial={{ opacity: 0, x: 20 }} 
                    animate={{ opacity: 1, x: 0 }}
                    className={`geo-card ${a.level}`}
                  >
                    <div className="c-t">
                      <span className="p">{a.level}</span>
                      <span className="s">{a.source}</span>
                    </div>
                    <div className="c-b">{a.message}</div>
                    <div className="c-f">COORD: {a.lat.toFixed(2)}, {a.lon.toFixed(2)}</div>
                  </motion.div>
                ))}
              </AnimatePresence>
           </div>
        </section>
      </main>

      <footer className="geo-footer">
         <div className="f-l"><TerminalIcon size={12} /> <span>&gt; geopin encryption layer: enabled (AES-256)</span></div>
         <div className="f-r">OSIN Strategic Intelligence // 📍 Geo-Ops Active</div>
      </footer>
    </div>
  );
};

export default GeoIntelligenceCommandCenter;
