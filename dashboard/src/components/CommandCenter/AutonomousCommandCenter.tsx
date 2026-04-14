import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import * as THREE from 'three';
import { Activity, Shield, Cpu, Zap, Send, Play, Terminal as TerminalIcon, Globe as GlobeIcon, Bot, Database } from 'lucide-react';
import { Alert, ChatMessage, SystemStatus, LLMResponse } from '../../types/command_center';
import './AutonomousCommandCenter.css';

const AutonomousCommandCenter: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [timeIndex, setTimeIndex] = useState(3);
  const [chat, setChat] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({
    llmBackend: 'CONNECTED',
    satelliteLayer: 'ACTIVE',
    graphDatabase: 'SYNCING',
    autonomousMode: 'STANDBY',
    propagationEngine: 'READY'
  });

  const globeRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene>();
  const rendererRef = useRef<THREE.WebGLRenderer>();
  const cameraRef = useRef<THREE.PerspectiveCamera>();
  const earthRef = useRef<THREE.Mesh>();
  const markersRef = useRef<THREE.Mesh[]>([]);
  const agentIntervalRef = useRef<NodeJS.Timeout>();

  // 1. Scene Initialization (NASA Texture)
  useEffect(() => {
    if (!globeRef.current) return;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, globeRef.current.clientWidth / globeRef.current.clientHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });

    renderer.setSize(globeRef.current.clientWidth, globeRef.current.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    globeRef.current.appendChild(renderer.domElement);

    const textureLoader = new THREE.TextureLoader();
    // Use NASA High-Res Texture
    const earthTexture = textureLoader.load('https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg');
    const geometry = new THREE.SphereGeometry(5, 64, 64);
    const material = new THREE.MeshPhongMaterial({ map: earthTexture, specular: 0x333333, shininess: 5 });
    const earth = new THREE.Mesh(geometry, material);
    scene.add(earth);

    // Atmospheric Glow
    const glowGeo = new THREE.SphereGeometry(5.12, 64, 64);
    const glowMat = new THREE.MeshBasicMaterial({ color: 0x0077ff, transparent: true, opacity: 0.1, side: THREE.BackSide });
    scene.add(new THREE.Mesh(glowGeo, glowMat));

    scene.add(new THREE.AmbientLight(0xffffff, 0.5));
    const dirLight = new THREE.DirectionalLight(0xffffff, 1);
    dirLight.position.set(5, 3, 5);
    scene.add(dirLight);

    camera.position.z = 14;

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
      if (agentIntervalRef.current) clearInterval(agentIntervalRef.current);
    };
  }, []);

  // 2. Data Logic & Persistence
  useEffect(() => {
    const generateIntelligence = () => {
      const newAlerts: Alert[] = [];
      const count = timeIndex * 4;
      for (let i = 0; i < count; i++) {
        newAlerts.push({
          id: `auton-${Date.now()}-${i}`,
          level: ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'][Math.floor(Math.random() * 4)] as any,
          message: `Autonomous Node Detected in Sector ${i+1}`,
          lat: Math.random() * 160 - 80,
          lon: Math.random() * 320 - 160,
          timestamp: new Date(),
          source: 'AGENT-SWARM',
          confidence: 0.95,
          type: 'intelligence'
        });
      }
      setAlerts(newAlerts);
      updateMarkers(newAlerts);
    };
    generateIntelligence();
  }, [timeIndex]);

  const updateMarkers = (alerts: Alert[]) => {
    if (!sceneRef.current) return;
    markersRef.current.forEach(m => sceneRef.current?.remove(m));
    markersRef.current = [];

    alerts.forEach(a => {
      const g = new THREE.SphereGeometry(0.12, 16, 16);
      const color = a.level === 'CRITICAL' ? 0xff0000 : a.level === 'HIGH' ? 0xffaa00 : 0x00ff00;
      const m = new THREE.Mesh(g, new THREE.MeshBasicMaterial({ color }));
      
      const phi = (90 - a.lat) * Math.PI / 180;
      const theta = (a.lon + 180) * Math.PI / 180;
      const r = 5.05;
      m.position.set(-r * Math.sin(phi) * Math.cos(theta), r * Math.cos(phi), r * Math.sin(phi) * Math.sin(theta));
      
      sceneRef.current?.add(m);
      markersRef.current.push(m);
    });
  };

  // 3. Simulated Backend Handlers
  const callLLM = async (prompt: string): Promise<LLMResponse> => {
    setSystemStatus(prev => ({ ...prev, llmBackend: 'PROCESSING' }));
    await new Promise(r => setTimeout(r, 1200));
    
    const responses: Record<string, string> = {
      'threat': 'Strategic posturing analysis: Higher signals in Eastern sectors. Recommend autonomous probe deployment.',
      'satellite': 'Satellite metadata cross-referenced. Thermal occlusions detected. Resolution improved to 0.5m.',
      'agent': 'Autonomous agent swarm syncing. Multi-vector intelligence correlations found in Graph Core.',
      'default': 'Command ingested. OSIN reasoning logic applied. System posture remain optimal.'
    };
    const key = Object.keys(responses).find(k => prompt.toLowerCase().includes(k)) || 'default';
    
    setSystemStatus(prev => ({ ...prev, llmBackend: 'CONNECTED' }));
    return { response: responses[key], confidence: 0.98, recommendations: ['Verify SIGINT', 'Deploy Probes'] };
  };

  const handleCommand = async () => {
    if (!chat.trim()) return;
    const msg = chat.trim();
    setMessages(prev => [...prev, { role: 'user', text: msg, timestamp: new Date() }]);
    setChat('');
    const res = await callLLM(msg);
    setMessages(prev => [...prev, { role: 'agent', text: res.response, timestamp: new Date() }]);
  };

  const toggleAutonomous = () => {
    if (systemStatus.autonomousMode === 'ACTIVE') {
      if (agentIntervalRef.current) clearInterval(agentIntervalRef.current);
      setSystemStatus(prev => ({ ...prev, autonomousMode: 'STANDBY' }));
      setMessages(prev => [...prev, { role: 'system', text: '> Autonomous agent loop suspended.', timestamp: new Date() }]);
    } else {
      setSystemStatus(prev => ({ ...prev, autonomousMode: 'ACTIVE' }));
      setMessages(prev => [...prev, { role: 'system', text: '> Initiating autonomous swarm logic...', timestamp: new Date() }]);
      agentIntervalRef.current = setInterval(async () => {
        const res = await callLLM('agent');
        setMessages(prev => [...prev, { role: 'agent', text: `[Agent-Self-Analysis]: ${res.response}`, timestamp: new Date() }]);
      }, 15000);
    }
  };

  const runPropagation = async () => {
    setSystemStatus(prev => ({ ...prev, propagationEngine: 'RUNNING' }));
    setMessages(prev => [...prev, { role: 'system', text: '> Starting propagation spread simulation...', timestamp: new Date() }]);
    await new Promise(r => setTimeout(r, 3000));
    setMessages(prev => [...prev, { role: 'agent', text: 'Propagation complete. 36% risk inflation in Sector 7 detected.', timestamp: new Date() }]);
    setSystemStatus(prev => ({ ...prev, propagationEngine: 'COMPLETE' }));
  };

  return (
    <div className="auton-center">
      <header className="auton-header">
        <div className="auton-branding">
          <GlobeIcon className="auton-logo" />
          <div className="auton-title">
            <h1>Autonomous Intelligence Core</h1>
            <span>LLM Integrated // NASA Texture // Agent Loop // v8.0.0</span>
          </div>
        </div>
        <div className="system-overview">
           <div className="overview-item"><span>LLM</span> <span className={systemStatus.llmBackend}>{systemStatus.llmBackend}</span></div>
           <div className="overview-item"><span>AGENT</span> <span className={systemStatus.autonomousMode}>{systemStatus.autonomousMode}</span></div>
        </div>
      </header>

      <div className="auton-time-control">
         <div className="t-label">Timeline Orchestrator: T{timeIndex}</div>
         <input type="range" min="1" max="5" value={timeIndex} onChange={(e) => setTimeIndex(Number(e.target.value))} className="t-slider" />
         <div className="t-markers">
            <span>Historical</span>
            <span>Recent</span>
            <span>Current</span>
            <span>Future</span>
            <span>Proj.</span>
         </div>
      </div>

      <main className="auton-body">
         {/* Left: Core Status */}
         <section className="col-core">
            <div className="p-label">Operational Core registry</div>
            <div className="core-grid">
               <div className="grid-item"><span>Satellite</span> <span className="active">ACTIVE</span></div>
               <div className="grid-item"><span>Graph DB</span> <span className="syncing">SYNCING</span></div>
               <div className="grid-item"><span>Prop. Eng</span> <span className="ready">{systemStatus.propagationEngine}</span></div>
            </div>
            
            <div className="core-actions">
               <button className={`action-btn ${systemStatus.propagationEngine}`} onClick={runPropagation}>
                  <Zap size={14} /> <span>Run Propagation</span>
               </button>
               <button className={`action-btn agent ${systemStatus.autonomousMode}`} onClick={toggleAutonomous}>
                  <Bot size={14} /> <span>{systemStatus.autonomousMode === 'ACTIVE' ? 'Suspend Agent' : 'Start Agent Loop'}</span>
               </button>
            </div>

            <div className="core-stats">
               <div className="s-row"><span>Intel Density</span> <span>{alerts.length * 10}%</span></div>
               <div className="s-row"><span>Causal links</span> <span>{alerts.length * 2}</span></div>
            </div>
         </section>

         {/* Center: HQ Globe */}
         <section className="col-globe">
            <div ref={globeRef} className="hq-globe-box" />
         </section>

         {/* Right: AI Nexus */}
         <section className="col-nexus">
            <div className="p-label">AI Intelligence Nexus</div>
            <div className="nexus-chat">
               <AnimatePresence>
                 {messages.map((m, i) => (
                   <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className={`msg ${m.role}`}>
                      <div className="m-h">{m.role.toUpperCase()} // {m.timestamp.toLocaleTimeString()}</div>
                      <div className="m-b">{m.text}</div>
                   </motion.div>
                 ))}
               </AnimatePresence>
            </div>
            <div className="nexus-input">
               <input type="text" value={chat} onChange={(e) => setChat(e.target.value)} onKeyPress={(e) => e.key === 'Enter' && handleCommand()} placeholder="Ingest command..." />
               <button onClick={handleCommand}><Send size={14} /></button>
            </div>
         </section>
      </main>

      <footer className="auton-footer">
         <div className="f-left"><TerminalIcon size={12} /> &gt; autonomous agent swarm: online and indexing {alerts.length} geo-nodes.</div>
         <div className="f-right">OSIN Project // Level 100 Autonomous OS // TRANSCENDENCE</div>
      </footer>
    </div>
  );
};

export default AutonomousCommandCenter;
