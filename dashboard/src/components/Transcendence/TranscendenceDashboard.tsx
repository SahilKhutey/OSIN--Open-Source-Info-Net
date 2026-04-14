import React, { useState, useEffect, Suspense } from 'react';
import { motion } from 'framer-motion';
import { Canvas } from '@react-three/fiber';
import TranscendentEarth from './TranscendentEarth';
import HexGridLoading from '../common/HexGridLoading';
import CognitiveMetrics from './CognitiveMetrics';
import TranscendenceTerminal from './TranscendenceTerminal';
import { ConsciousnessState, OperationalMode } from '../../types/transcendence';
import ErrorBoundary from '../common/ErrorBoundary';

const TranscendenceDashboard: React.FC = () => {
  const [currentMode, setCurrentMode] = useState<OperationalMode>('COMMAND_CENTER');

  const [consciousnessState, setConsciousnessState] = useState<ConsciousnessState>({
    confidence: 0.92,
    uncertainty: 0.08,
    strategicFocus: 0.88,
    cognitiveLoad: 0.75,
    missionProgress: 1.0
  });

  // Simulation loop for metrics
  useEffect(() => {
    const timer = setInterval(() => {
      setConsciousnessState(prev => ({
        ...prev,
        confidence: Math.min(0.98, prev.confidence + (Math.random() - 0.5) * 0.01),
        uncertainty: Math.max(0.02, prev.uncertainty + (Math.random() - 0.5) * 0.005),
        strategicFocus: Math.min(0.95, prev.strategicFocus + (Math.random() - 0.5) * 0.01),
        cognitiveLoad: 0.6 + Math.random() * 0.2,
      }));
    }, 5000);
    return () => clearInterval(timer);
  }, []);

  const getModeDisplay = (mode: OperationalMode): string => {
    const modes = {
      'COMMAND_CENTER': '🚀 Command Center',
      'SATELLITE_OPS': '🛰️ Satellite Ops',
      'GEO_INTELLIGENCE': '📍 Geo-Intelligence',
      'TIME_TRAVEL': '⏳ Time-Travel',
      'AUTONOMOUS_CORE': '🤖 Autonomous Core'
    };
    return modes[mode];
  };

  return (
    <div className="h-full w-full flex flex-col p-8 tactical-scroll overflow-auto">
      {/* HUD Header */}
      <header className="flex justify-between items-start mb-8 border-b border-white/5 pb-6">
        <div>
           <h1 className="text-4xl font-black font-tactical text-osin-emerald tracking-tighter mb-2 drop-shadow-[0_0_15px_rgba(16,185,129,0.3)]">
             OSIN_TRANSCENDENCE <span className="text-osin-cyan opacity-80 text-xl font-mono tracking-normal ml-2">v8.0.0</span>
           </h1>
           <p className="text-[10px] text-gray-500 font-mono uppercase tracking-[0.4em] flex items-center gap-3">
              <span className="w-2 h-2 rounded-full bg-osin-emerald animate-pulse" />
              Autonomous Consciousness Core • Real-time Logic Sync
           </p>
        </div>
        
        <div className="flex gap-4">
          <div className="text-right">
             <div className="text-xs font-black font-tactical text-osin-emerald mb-1">MISSION_STATUS</div>
             <div className="text-[10px] text-gray-600 uppercase font-mono tracking-widest bg-white/5 px-2 py-1 rounded border border-white/5">Phase 45 Verified</div>
          </div>
        </div>
      </header>

      {/* STRATEGIC GRID */}
      <div className="flex-1 grid grid-cols-12 gap-6 min-h-0">
        
        {/* PANEL LEFT: Consciousness Metrics (Col-3) */}
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="col-span-12 xl:col-span-3 flex flex-col gap-6"
        >
          <div className="glass-panel flex-1 flex flex-col border-osin-cyan/20">
            <div className="p-4 border-b border-white/5 flex justify-between items-center">
              <h2 className="text-xs font-bold font-tactical text-osin-cyan">Cognitive_Fabric</h2>
              <span className="text-[8px] bg-osin-cyan/10 text-osin-cyan px-2 py-0.5 rounded uppercase font-bold animate-flicker">Sync_Active</span>
            </div>
            
            <div className="p-6 flex-1 flex flex-col">
              <div className="space-y-4 mb-8">
                {[
                  { label: 'Neural Density', val: 'BERT+NWX', color: 'text-osin-emerald' },
                  { label: 'Decision Gate', val: 'Operational', color: 'text-osin-emerald' },
                  { label: 'Safety Buffer', val: 'Engaged', color: 'text-yellow-500' }
                ].map((item, i) => (
                  <div key={i} className="flex justify-between items-center bg-white/5 p-3 rounded-xl border border-white/5">
                    <span className="text-[10px] text-gray-500 uppercase font-tactical tracking-widest">{item.label}</span>
                    <span className={`${item.color} text-[10px] font-black uppercase`}>{item.val}</span>
                  </div>
                ))}
              </div>

              <div className="flex-1 min-h-[300px]">
                <CognitiveMetrics state={consciousnessState} />
              </div>

              <div className="mt-8 pt-6 border-t border-white/5 space-y-3">
                 <button className="w-full py-3 bg-red-500/5 hover:bg-red-500/10 border border-red-500/20 text-red-500 text-[10px] uppercase font-black transition-all rounded-xl active:scale-95">Pause Autonomy</button>
                 <button className="w-full py-3 bg-white/5 hover:bg-white/10 border border-white/10 text-gray-400 text-[10px] uppercase font-black transition-all rounded-xl active:scale-95">Cognitive Reset</button>
              </div>
            </div>
          </div>
        </motion.div>

        {/* PANEL CENTER: World View (Col-6) */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          className="col-span-12 xl:col-span-6 flex flex-col"
        >
          <div className="glass-panel flex-1 relative overflow-hidden group shadow-[0_0_100px_rgba(16,185,129,0.05)]">
            <div className="absolute top-6 left-6 z-10 p-4 bg-black/60 backdrop-blur-md border border-white/10 rounded-2xl">
               <h2 className="text-xl font-black font-tactical text-osin-emerald tracking-tighter">TRANSCENDENT EARTH</h2>
               <div className="flex gap-2 mt-2">
                 <span className="text-[8px] bg-osin-emerald/10 text-osin-emerald px-1.5 py-0.5 rounded border border-osin-emerald/30 uppercase font-bold">L4 Telemetry</span>
                 <span className="text-[8px] bg-osin-purple/10 text-osin-purple px-1.5 py-0.5 rounded border border-osin-purple/30 uppercase font-bold">Atmospheric Glow</span>
               </div>
            </div>

            <div className="w-full h-full relative cursor-move">
              <ErrorBoundary fallback={
                <div className="w-full h-full flex flex-col items-center justify-center bg-gray-900/40 rounded-2xl border border-red-500/20">
                   <div className="text-red-500 text-6xl mb-4 opacity-50">⚠️</div>
                   <div className="text-red-400 font-tactical text-xs font-black uppercase tracking-widest">3D Visual Engine Crushed</div>
                   <div className="text-gray-500 text-[10px] mt-2 font-mono">CODE: CORE_FAIL_V8</div>
                </div>
              }>
                <Suspense fallback={<HexGridLoading />}>
                  <Canvas camera={{ position: [0, 0, 16], fov: 60 }}>
                    <TranscendentEarth />
                  </Canvas>
                </Suspense>
              </ErrorBoundary>
            </div>

            <div className="absolute bottom-6 left-6 right-6 z-10">
              <div className="glass-panel p-2 flex gap-2 border-white/5 bg-black/40 backdrop-blur-3xl">
                {([
                  'COMMAND_CENTER',
                  'SATELLITE_OPS', 
                  'GEO_INTELLIGENCE',
                  'TIME_TRAVEL',
                  'AUTONOMOUS_CORE'
                ] as OperationalMode[]).map((mode) => (
                  <button
                    key={mode}
                    onClick={() => setCurrentMode(mode)}
                    className={`flex-1 py-4 px-2 rounded-xl text-[9px] font-tactical font-black transition-all duration-300 uppercase tracking-tighter ${
                      currentMode === mode
                        ? 'bg-osin-emerald text-black shadow-[0_0_20px_rgba(16,185,129,0.4)]'
                        : 'bg-white/5 text-gray-500 hover:text-white hover:bg-white/10 border border-white/5 opacity-60'
                    }`}
                  >
                    {getModeDisplay(mode)}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </motion.div>

        {/* PANEL RIGHT: Tactical Feed (Col-3) */}
        <motion.div 
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="col-span-12 xl:col-span-3 flex flex-col gap-6"
        >
          <div className="glass-panel p-6 border-osin-purple/20">
            <h2 className="text-xs font-bold font-tactical text-osin-purple mb-4">Ascension_Protocol</h2>
            <div className="relative h-1.5 w-full bg-white/5 rounded-full overflow-hidden mb-8 shadow-inner">
              <motion.div 
                className="absolute inset-0 bg-gradient-to-r from-osin-emerald to-osin-cyan shadow-[0_0_15px_rgba(16,185,129,0.6)]"
                initial={{ width: 0 }}
                animate={{ width: '100%' }}
                transition={{ duration: 3, delay: 0.5 }}
              />
            </div>
            
            <div className="space-y-3">
              {[
                { label: 'Neural Synapse', status: 'Active', color: 'text-osin-emerald' },
                { label: 'Graph Ingress', status: 'Synced', color: 'text-osin-emerald' },
                { label: 'Global Guard', status: 'Engaged', color: 'text-yellow-500' },
                { label: 'God Mode Unit', status: 'Verified', color: 'text-osin-purple' },
              ].map((item, i) => (
                <div key={i} className="flex justify-between items-center group bg-white/5 p-2 rounded-lg hover:bg-white/10 transition-colors">
                  <span className="text-[10px] text-gray-500 uppercase font-tactical tracking-widest">{item.label}</span>
                  <span className={`${item.color} text-[10px] font-black uppercase tracking-tighter`}>{item.status}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="glass-panel flex-1 flex flex-col min-h-[300px]">
            <TranscendenceTerminal />
          </div>
        </motion.div>
      </div>
      
      {/* FOOTER BAR */}
      <motion.div 
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="text-[9px] text-gray-600 flex justify-between items-center font-mono opacity-50 uppercase tracking-[0.2em]"
      >
        <span>OSIN_TRANSCENDENCE_SYSTEM_NODE_8.0.0_PRODUCTION_CORE</span>
        <div className="flex gap-4">
          <span>COORDINATES: [+0.000, -0.000]</span>
          <span>UPTIME: 99.999%</span>
        </div>
      </motion.div>
    </div>
  );
};

export default TranscendenceDashboard;
