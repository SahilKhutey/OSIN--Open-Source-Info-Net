import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import * as THREE from 'three';
import { Activity, Shield, Cpu, Clock, Send, Play, FastForward, RotateCcw, MessageSquare, Terminal as TerminalIcon } from 'lucide-react';
import { Alert, GraphConnection, TimeIndex, ChatMessage, SystemStatus } from '../../types/command_center';
import './AdvancedCommandCenter.css';

const AdvancedCommandCenter: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [connections, setConnections] = useState<GraphConnection[]>([]);
  const [timeIndex, setTimeIndex] = useState<TimeIndex>(1);
  const [chat, setChat] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({
    ingestion: 'ACTIVE',
    graphCore: 'ONLINE',
    aiReasoning: 'STABLE',
    threatLevel: 'NORMAL',
    globalRisk: 22,
    voiceAnalyst: 'ONLINE',
    simulation: 'READY',
    aiCommand: 'ONLINE',
    timeTravel: 'ACTIVE'
  });

  const globeRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene>();
  const rendererRef = useRef<THREE.WebGLRenderer>();
  const cameraRef = useRef<THREE.PerspectiveCamera>();
  const earthRef = useRef<THREE.Mesh>();
  const markersRef = useRef<THREE.Mesh[]>([]);
  const connectionsRef = useRef<THREE.Line[]>([]);

  // 1. Scene Initialization
  useEffect(() => {
    if (!globeRef.current) return;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, globeRef.current.clientWidth / globeRef.current.clientHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });

    renderer.setSize(globeRef.current.clientWidth, globeRef.current.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    globeRef.current.appendChild(renderer.domElement);

    const textureLoader = new THREE.TextureLoader();
    const earthTexture = textureLoader.load('https://unpkg.com/three-globe/example/img/earth-night.jpg');
    const geometry = new THREE.SphereGeometry(5, 64, 64);
    const material = new THREE.MeshPhongMaterial({ map: earthTexture, specular: 0x333333, shininess: 5 });
    const earth = new THREE.Mesh(geometry, material);
    scene.add(earth);

    scene.add(new THREE.AmbientLight(0xffffff, 0.4));
    const dirLight = new THREE.DirectionalLight(0xa855f7, 1);
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
    };
  }, []);

  // 2. Temporal Data Loading
  useEffect(() => {
    const timeAlerts: Alert[] = [];
    const timeConnections: GraphConnection[] = [];
    const alertCount = timeIndex * 5;

    for (let i = 0; i < alertCount; i++) {
      const alert: Alert = {
        id: `t${timeIndex}-${i}`,
        level: ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'][Math.floor(Math.random() * 4)] as any,
        message: `T${timeIndex} Sequence Node ${i+1}`,
        msg: `Event ${i+1} Verified`,
        lat: Math.random() * 160 - 80,
        lon: Math.random() * 320 - 160,
        timestamp: new Date(),
        source: 'TEMPORAL-SIM',
        confidence: 0.9,
        type: 'simulation_node',
        timeIndex: timeIndex
      };
      timeAlerts.push(alert);
    }

    for (let i = 0; i < timeAlerts.length - 1; i++) {
        if (Math.random() > 0.5) {
            timeConnections.push({
                id: `c-${timeIndex}-${i}`,
                from: timeAlerts[i].id,
                to: timeAlerts[i+1].id,
                strength: Math.random(),
                type: 'propagation_link',
                timeIndex: timeIndex
            });
        }
    }

    setAlerts(timeAlerts);
    setConnections(timeConnections);
  }, [timeIndex]);

  // 3. Globe Visualization Update
  useEffect(() => {
    if (!sceneRef.current) return;

    markersRef.current.forEach(m => sceneRef.current?.remove(m));
    connectionsRef.current.forEach(l => sceneRef.current?.remove(l));
    markersRef.current = [];
    connectionsRef.current = [];

    const getPos = (lat: number, lon: number) => {
      const phi = (90 - lat) * Math.PI / 180;
      const theta = (lon + 180) * Math.PI / 180;
      const r = 5.05;
      return new THREE.Vector3(-r * Math.sin(phi) * Math.cos(theta), r * Math.cos(phi), r * Math.sin(phi) * Math.sin(theta));
    };

    alerts.forEach(a => {
      const g = new THREE.SphereGeometry(0.15, 16, 16);
      const color = a.level === 'CRITICAL' ? 0xef4444 : a.level === 'HIGH' ? 0xf97316 : 0xa855f7;
      const m = new THREE.Mesh(g, new THREE.MeshBasicMaterial({ color }));
      m.position.copy(getPos(a.lat, a.lon));
      sceneRef.current?.add(m);
      markersRef.current.push(m);
    });

    connections.forEach(c => {
      const from = alerts.find(a => a.id === c.from);
      const to = alerts.find(a => a.id === c.to);
      if (from && to) {
        const geo = new THREE.BufferGeometry().setFromPoints([getPos(from.lat, from.lon), getPos(to.lat, to.lon)]);
        const line = new THREE.Line(geo, new THREE.LineBasicMaterial({ color: 0xa855f7, transparent: true, opacity: 0.3 }));
        sceneRef.current?.add(line);
        connectionsRef.current.push(line);
      }
    });

  }, [alerts, connections]);

  const simulatePropagation = () => {
    setSystemStatus(prev => ({ ...prev, simulation: 'RUNNING' }));
    const step = (idx: number) => {
      if (idx <= 4) {
        setTimeIndex(idx as TimeIndex);
        setTimeout(() => step(idx + 1), 1000);
      } else {
        setSystemStatus(prev => ({ ...prev, simulation: 'COMPLETE' }));
      }
    };
    step(1);
  };

  const handleCommand = () => {
    if (!chat.trim()) return;
    const userMsg = chat.trim();
    setMessages(prev => [...prev, { role: 'user', text: userMsg, timestamp: new Date() }]);
    setChat('');
    setSystemStatus(prev => ({ ...prev, aiCommand: 'PROCESSING' }));

    setTimeout(() => {
      let response = "COMMAND RECOGNIZED. DATA ANALYTICS IN PROGRESS.";
      const cmd = userMsg.toLowerCase();
      if (cmd.includes('propagate')) { response = "INITIATING TEMPORAL PROPAGATION SIMULATION."; simulatePropagation(); }
      else if (cmd.includes('past')) { setTimeIndex(1); response = "TIME INDEX SET TO T1 (PAST)."; }
      else if (cmd.includes('future')) { setTimeIndex(4); response = "TIME INDEX SET TO T4 (PROJECTED FUTURE)."; }

      setMessages(prev => [...prev, { role: 'ai', text: response, timestamp: new Date() }]);
      setSystemStatus(prev => ({ ...prev, aiCommand: 'ONLINE' }));
    }, 1000);
  };

  return (
    <div className="adv-command-center">
      <header className="adv-header">
        <div className="adv-branding">
          <Clock className="adv-logo" />
          <div className="adv-title">
            <h1>Advanced Strategic Command</h1>
            <span>Time-Travel Replay + AI Command // God Mode Phase</span>
          </div>
        </div>
        <div className="temporal-state">
           <div className={`mode-badge ${systemStatus.timeTravel}`}>TIME TRAVEL {systemStatus.timeTravel}</div>
           <div className={`mode-badge ${systemStatus.aiCommand}`}>AI COMMAND {systemStatus.aiCommand}</div>
        </div>
      </header>

      <div className="adv-timeline-bar">
         <div className="t-label">Strategic Timeline Index: T{timeIndex}</div>
         <input type="range" min="1" max="4" value={timeIndex} onChange={(e) => setTimeIndex(Number(e.target.value) as TimeIndex)} className="t-slider" />
         <div className="t-markers">
            <span>PAST</span>
            <span>RECENT</span>
            <span>PRESENT</span>
            <span>PROJECTION</span>
         </div>
      </div>

      <main className="adv-grid">
         {/* Left: System Status */}
         <section className="col-status">
            <div className="p-header">Core Infrastructure Registry</div>
            <div className="status-v-list">
               <div className="v-item"><span>Ingestion</span> <span className="green">ONLINE</span></div>
               <div className="v-item"><span>Graph Core</span> <span className="green">ONLINE</span></div>
               <div className="v-item"><span>Simulation</span> <span className={systemStatus.simulation === 'RUNNING' ? 'amber' : 'green'}>{systemStatus.simulation}</span></div>
            </div>
            <button className={`sim-trigger ${systemStatus.simulation}`} onClick={simulatePropagation}>
                <FastForward size={14} /> <span>Simulate Propagation</span>
            </button>
            <div className="risk-widget">
               <div className="r-label">Temporal Risk: {timeIndex * 15}%</div>
               <div className="r-bar"><div className="fill" style={{ width: `${timeIndex * 15}%` }} /></div>
            </div>
         </section>

         {/* Center: Globe View */}
         <section className="col-center">
            <div ref={globeRef} className="v-globe-box" />
         </section>

         {/* Right: AI Chat */}
         <section className="col-ai">
            <div className="p-header">AI Mission Command</div>
            <div className="chat-viewport">
               {messages.map((m, i) => (
                 <div key={i} className={`chat-msg ${m.role}`}>
                    <div className="m-header">{m.role === 'user' ? 'OPERATOR' : 'OSIN AI'} // {m.timestamp.toLocaleTimeString()}</div>
                    <div className="m-body">{m.text}</div>
                 </div>
               ))}
            </div>
            <div className="chat-input-box">
               <input 
                 type="text" 
                 value={chat} 
                 onChange={(e) => setChat(e.target.value)} 
                 onKeyPress={(e) => e.key === 'Enter' && handleCommand()}
                 placeholder="Enter mission command..." 
               />
               <button onClick={handleCommand}><Send size={14} /></button>
            </div>
         </section>
      </main>

      <footer className="adv-footer">
         <div className="f-left"><TerminalIcon size={12} /> &gt; temporal intelligence index T{timeIndex} loading complete.</div>
         <div className="f-right">OSIN Project // Strategic Tier 100 // God Mode</div>
      </footer>
    </div>
  );
};

export default AdvancedCommandCenter;
