import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, Zap, Globe, Activity, MessageSquare, Terminal as TerminalIcon, Maximize2, Menu } from 'lucide-react';

import GlobeVisualization from './GlobeVisualization';
import ThreatFeed from './ThreatFeed';
import SystemStatus from './SystemStatus';
import Terminal from './Terminal';
import AIChatAssistant from './AIChatAssistant';
import { useIntelligenceData } from '../../hooks/useIntelligenceData';
import { Alert, SystemStatus as SystemStatusType } from '../../types/command_center';

const OSINCommandCenter: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [isAIAssistantOpen, setIsAIAssistantOpen] = useState(false);
  const [terminalOutput, setTerminalOutput] = useState<string[]>([
    'OSIN CORE INITIALIZATION SEQUENCE INITIATED...',
    'CONNECTING TO GLOBAL SIGNAL MESH...',
    'AUTHENTICATING GRAPH CORE HANDLER...',
    'WAR ROOM UPTIME: 0.00ms',
    'ALL SYSTEMS NOMINAL.'
  ]);

  const intelligenceData = useIntelligenceData();

  const [systemStatus, setSystemStatus] = useState<SystemStatusType>({
    ingestion: 'ACTIVE',
    graphCore: 'ONLINE',
    aiReasoning: 'STABLE',
    threatLevel: 'NORMAL',
    globalRisk: 24
  });

  // Simulation loop for live intelligence
  useEffect(() => {
    const alertInterval = setInterval(() => {
      const levels: Array<Alert['level']> = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
      const sources = ['CYBER', 'GEO', 'SIGNAL', 'SOCIAL', 'CIV'];
      const level = levels[Math.floor(Math.random() * 4)];
      
      const newAlert: Alert = {
        id: `alert-${Date.now()}`,
        level,
        message: generateRandomAlertMessage(level),
        location: {
          lat: Math.random() * 180 - 90,
          lon: Math.random() * 360 - 180
        },
        timestamp: new Date(),
        source: sources[Math.floor(Math.random() * sources.length)],
        confidence: Math.random() * 0.4 + 0.6
      };
      
      setAlerts(prev => [newAlert, ...prev].slice(0, 30));
      addTerminalOutput(`[${newAlert.level}] ${newAlert.message}`);
      
      // Update risk based on critical alerts
      if (level === 'CRITICAL' || level === 'HIGH') {
        setSystemStatus(prev => ({
          ...prev,
          globalRisk: Math.min(95, prev.globalRisk + 5),
          threatLevel: level === 'CRITICAL' ? 'CRITICAL' : 'HIGH'
        }));
      }
    }, 4000);

    return () => clearInterval(alertInterval);
  }, []);

  const generateRandomAlertMessage = (level: string): string => {
    const critical = ['CRITICAL GRID SECTOR FAILURE', 'RANSOMWARE BARRAGE DETECTED', 'COORDINATED STATE-ACTOR ATTACK'];
    const medium = ['Unusual Signal Density Spike', 'Domain Registration Anomaly', 'Dark Web Mention of Asset X'];
    const low = ['Routine scan complete', 'Policy update synchronized', 'Node 82 latency check'];
    
    if (level === 'CRITICAL') return critical[Math.floor(Math.random() * critical.length)];
    if (level === 'MEDIUM') return medium[Math.floor(Math.random() * medium.length)];
    return low[Math.floor(Math.random() * low.length)];
  };

  const addTerminalOutput = (message: string) => {
    setTerminalOutput(prev => [...prev, message].slice(-50));
  };

  const handleAlertClick = (alert: Alert) => {
    setSelectedAlert(alert);
    addTerminalOutput(`ANALYST SELECTION: Examining ${alert.id} - ${alert.message}`);
  };

  return (
    <div className="min-h-screen bg-[#020408] text-white font-mono selection:bg-cyan-500/30 overflow-hidden flex flex-col">
      {/* 1. TOP NAVIGATION BAR */}
      <header className="h-16 border-b border-white/5 bg-black/40 backdrop-blur-md flex items-center justify-between px-6 shrink-0 relative z-50">
        <div className="flex items-center gap-8">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-cyan-500/10 border border-cyan-500/30 rounded flex items-center justify-center">
              <Shield className="text-cyan-500" size={18} />
            </div>
            <div>
              <h1 className="text-sm font-bold tracking-[0.3em] uppercase">OSIN Command</h1>
              <div className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
                <span className="text-[9px] text-green-500/80 uppercase tracking-widest">System Synchronized</span>
              </div>
            </div>
          </div>
          
          <nav className="hidden md:flex items-center gap-6">
             <div className="h-4 w-px bg-white/10" />
             {['Tactical', 'Strategic', 'Geopolitical', 'Network'].map(item => (
               <button key={item} className="text-[10px] uppercase tracking-widest opacity-40 hover:opacity-100 transition-opacity">
                 {item}
               </button>
             ))}
          </nav>
        </div>

        <div className="flex items-center gap-6">
          <div className="flex flex-col items-end">
            <span className="text-[10px] opacity-40 uppercase tracking-tighter">Current Threat Level</span>
            <span className={`text-[10px] font-bold uppercase tracking-widest ${
              systemStatus.threatLevel === 'CRITICAL' ? 'text-rose-500' : 'text-cyan-500'
            }`}>
              {systemStatus.threatLevel}
            </span>
          </div>
          <button 
            onClick={() => setIsAIAssistantOpen(!isAIAssistantOpen)}
            className="flex items-center gap-2 px-4 py-2 bg-cyan-500/10 border border-cyan-500/20 rounded-lg hover:bg-cyan-500/20 transition-all group"
          >
            <Zap size={14} className="text-cyan-500 group-hover:scale-125 transition-transform" />
            <span className="text-[10px] uppercase font-bold tracking-widest">AI Analyst</span>
          </button>
        </div>
      </header>

      {/* 2. MAIN CONTENT GRID */}
      <main className="flex-1 p-6 gap-6 grid grid-cols-12 overflow-hidden">
        
        {/* LEFT: STATUS & TERMINAL */}
        <div className="col-span-12 lg:col-span-3 flex flex-col gap-6 overflow-hidden">
          <div className="flex-1 bg-black/40 border border-white/5 rounded-2xl p-6 backdrop-blur-sm">
            <SystemStatus status={systemStatus} />
          </div>
          <div className="h-[250px] shrink-0">
            <Terminal output={terminalOutput} />
          </div>
        </div>

        {/* CENTER: 3D GLOBE & ANALYSIS */}
        <div className="col-span-12 lg:col-span-6 flex flex-col gap-6 overflow-hidden">
          <div className="flex-1 bg-black/40 border border-white/5 rounded-2xl p-6 backdrop-blur-sm relative group overflow-hidden">
            <div className="absolute top-6 left-6 z-10">
              <h2 className="text-xs font-bold tracking-widest uppercase opacity-60 flex items-center gap-2">
                <Globe size={14} />
                Global Surface Intelligence
              </h2>
            </div>
            <div className="absolute top-6 right-6 z-10 flex gap-2">
              <button className="p-2 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors">
                <Maximize2 size={14} className="opacity-60" />
              </button>
            </div>
            
            <div className="w-full h-full flex items-center justify-center">
              <GlobeVisualization 
                alerts={alerts}
                onAlertSelect={handleAlertClick}
                onGlobeClick={() => {}}
                className="w-full h-full"
              />
            </div>

            {/* Selected Alert Floating Panel */}
            <AnimatePresence>
              {selectedAlert && (
                <motion.div
                  initial={{ opacity: 0, y: 50, scale: 0.9 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 50, scale: 0.9 }}
                  className="absolute bottom-6 left-6 right-6 bg-cyan-950/20 border border-cyan-500/30 rounded-xl p-4 backdrop-blur-xl z-20"
                >
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="text-[10px] font-bold text-cyan-400 uppercase tracking-widest">Entity Investigation</h3>
                    <button onClick={() => setSelectedAlert(null)} className="opacity-40 hover:opacity-100">×</button>
                  </div>
                  <p className="text-xs font-medium mb-3">{selectedAlert.message}</p>
                  <div className="grid grid-cols-3 gap-4 border-t border-cyan-500/10 pt-3">
                    <div className="flex flex-col">
                      <span className="text-[8px] opacity-40 uppercase">Confidence</span>
                      <span className="text-[10px] font-mono">{(selectedAlert.confidence * 100).toFixed(1)}%</span>
                    </div>
                    <div className="flex flex-col">
                      <span className="text-[8px] opacity-40 uppercase">Coordinates</span>
                      <span className="text-[10px] font-mono">{selectedAlert.location?.lat.toFixed(2)}, {selectedAlert.location?.lon.toFixed(2)}</span>
                    </div>
                    <div className="flex flex-col">
                      <span className="text-[8px] opacity-40 uppercase">Source</span>
                      <span className="text-[10px] font-mono">{selectedAlert.source}</span>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* RIGHT: THREAT FEED */}
        <div className="col-span-12 lg:col-span-3 bg-black/40 border border-white/5 rounded-2xl p-6 backdrop-blur-sm overflow-hidden">
          <ThreatFeed alerts={alerts} onAlertClick={handleAlertClick} />
        </div>

      </main>

      {/* FOOTER STATS */}
      <footer className="h-10 border-t border-white/5 bg-black/60 px-6 flex items-center justify-between text-[8px] uppercase tracking-[0.2em] opacity-40 shrink-0">
        <div className="flex gap-8">
          <span>Active Nodes: 1,402</span>
          <span>Data Throughput: 4.8 GB/s</span>
          <span>Crypto-Hash: 8fA2...3C9d</span>
        </div>
        <div className="flex gap-4">
          <span>{new Date().toUTCString()}</span>
          <span>OSIN Project v8.0.0</span>
        </div>
      </footer>

      {/* AI ASSISTANT MODAL */}
      <AnimatePresence>
        {isAIAssistantOpen && (
          <AIChatAssistant onClose={() => setIsAIAssistantOpen(false)} />
        )}
      </AnimatePresence>

      <style>{`
        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.05); border-radius: 10px; }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.1); }
      `}</style>
    </div>
  );
};

export default OSINCommandCenter;
