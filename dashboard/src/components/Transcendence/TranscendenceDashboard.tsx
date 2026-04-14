import React, { useState, useEffect, Suspense } from 'react';
import { motion } from 'framer-motion';
import { Canvas } from '@react-three/fiber';
import TranscendentEarth from './TranscendentEarth';
import HexGridLoading from '../common/HexGridLoading';
import CognitiveMetrics from './CognitiveMetrics';
import TranscendenceTerminal from './TranscendenceTerminal';
import { ConsciousnessState, OperationalMode } from '../../types/transcendence';

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
    <div className="min-h-screen bg-black text-gray-100 font-mono p-6 overflow-hidden flex flex-col gap-6 selection:bg-osin-cyan/30">
      {/* HEADER - TRANSCENDENCE STATUS */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex justify-between items-start border-b border-osin-emerald/30 pb-4"
      >
        <div>
          <h1 className="text-4xl font-orbitron font-black tracking-tighter text-osin-emerald drop-shadow-[0_0_15px_rgba(16,185,129,0.4)] mb-2 uppercase">
            OSIN TRANSCENDENCE <span className="text-osin-cyan opacity-80 text-2xl">v8.0.0</span>
          </h1>
          <p className="text-sm text-gray-400 font-light flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-osin-emerald animate-pulse" />
            Autonomous Global Intelligence Operating System • Consciousness Core Active
          </p>
        </div>
        
        <div className="text-right flex flex-col items-end">
          <div className="text-osin-emerald font-orbitron font-bold text-xl tracking-widest">MISSION COMPLETE</div>
          <div className="text-[10px] text-gray-500 bg-gray-900/50 px-2 py-1 rounded border border-gray-800 mt-1 uppercase tracking-widest">
            ALL 45 PHASES VERIFIED
          </div>
        </div>
      </motion.div>

      {/* MAIN DASHBOARD GRID */}
      <div className="flex-1 grid grid-cols-12 gap-6 min-h-0">
        
        {/* LEFT COLUMN - COGNITIVE STATE */}
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="col-span-3 flex flex-col gap-6"
        >
          <div className="flex-1 p-5 rounded-2xl bg-gray-900/20 backdrop-blur-xl border border-gray-800 shadow-2xl flex flex-col">
            <h2 className="text-osin-cyan font-orbitron text-lg mb-6 flex justify-between items-center">
              CONSCIOUSNESS_CORE
              <span className="text-[10px] bg-osin-emerald/20 text-osin-emerald px-2 py-0.5 rounded-full animate-pulse uppercase">Active</span>
            </h2>
            
            <div className="space-y-4 text-xs">
              <div className="flex justify-between items-center group">
                <span className="text-gray-500 group-hover:text-gray-300 transition-colors">Cognitive Fabric:</span>
                <span className="text-osin-emerald font-bold">BERT + NetworkX</span>
              </div>
              <div className="flex justify-between items-center group">
                <span className="text-gray-500 group-hover:text-gray-300 transition-colors">Strategic Engine:</span>
                <span className="text-osin-emerald font-bold uppercase">Operational</span>
              </div>
              <div className="flex justify-between items-center group">
                <span className="text-gray-500 group-hover:text-gray-300 transition-colors">Safety Monitor:</span>
                <span className="text-yellow-500 font-bold uppercase tracking-tighter">Engaged</span>
              </div>
            </div>

            <div className="mt-8 flex-1">
              <CognitiveMetrics state={consciousnessState} />
            </div>

            <div className="mt-6 pt-6 border-t border-gray-800 space-y-3">
              <h3 className="text-red-500 text-[10px] font-orbitron uppercase tracking-widest mb-1 opacity-60">Emergency Overrides</h3>
              <button className="w-full py-2 bg-red-900/10 hover:bg-red-900/20 border border-red-900/50 text-red-500 text-[10px] uppercase font-bold transition-all rounded-lg active:scale-95">
                Pause Autonomy
              </button>
              <button className="w-full py-2 bg-blue-900/10 hover:bg-blue-900/20 border border-blue-900/50 text-blue-400 text-[10px] uppercase font-bold transition-all rounded-lg active:scale-95">
                Throttle Cognitive Load
              </button>
            </div>
          </div>
        </motion.div>

        {/* CENTER COLUMN - TRANSCENDENT EARTH */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4 }}
          className="col-span-6 flex flex-col gap-6 relative"
        >
          <div className="flex-1 rounded-2xl bg-black border border-gray-800 shadow-[0_0_50px_rgba(0,0,0,1)] relative overflow-hidden group">
            <div className="absolute top-4 left-4 z-10 p-4">
               <h2 className="text-osin-emerald font-orbitron text-xl drop-shadow-md">TRANSCENDENT EARTH</h2>
               <div className="flex gap-2 mt-2">
                 <span className="text-[9px] bg-osin-emerald/10 text-osin-emerald px-2 py-1 rounded border border-osin-emerald/20 uppercase">NASA Blue Marble</span>
                 <span className="text-[9px] bg-osin-purple/10 text-osin-purple px-2 py-1 rounded border border-osin-purple/20 uppercase">Atmospheric Bloom</span>
               </div>
            </div>

            <div className="w-full h-full relative cursor-move active:cursor-grabbing">
              <Suspense fallback={<HexGridLoading />}>
                <Canvas camera={{ position: [0, 0, 16], fov: 60 }}>
                  <TranscendentEarth />
                </Canvas>
              </Suspense>
            </div>

            <div className="absolute bottom-4 left-4 right-4 z-10">
              <div className="grid grid-cols-5 gap-2 backdrop-blur-md bg-black/20 p-2 rounded-xl border border-white/5">
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
                    className={`py-3 px-1 rounded-lg text-[9px] font-orbitron transition-all duration-300 uppercase tracking-tighter ${
                      currentMode === mode
                        ? 'bg-osin-emerald text-black font-black shadow-[0_0_15px_rgba(16,185,129,0.5)]'
                        : 'bg-gray-900/50 text-gray-500 hover:text-gray-300 hover:bg-gray-800/80 border border-gray-800'
                    }`}
                  >
                    {getModeDisplay(mode)}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </motion.div>

        {/* RIGHT COLUMN - MISSION & TERMINAL */}
        <motion.div 
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="col-span-3 flex flex-col gap-6"
        >
          {/* Mission Progress */}
          <div className="p-5 rounded-2xl bg-gray-900/20 backdrop-blur-xl border border-gray-800 shadow-2xl">
            <h2 className="text-osin-purple font-orbitron text-lg mb-4">ASCENSION_PROTOCOL</h2>
            <div className="relative h-1 w-full bg-gray-800 rounded-full overflow-hidden mb-6">
              <motion.div 
                className="absolute inset-0 bg-osin-emerald shadow-[0_0_10px_#10b981]"
                initial={{ width: 0 }}
                animate={{ width: '100%' }}
                transition={{ duration: 2, delay: 1 }}
              />
            </div>
            
            <div className="space-y-3">
              {[
                { label: 'Consciousness Core', status: 'ACTIVE', color: 'text-osin-emerald' },
                { label: 'Strategic Planning', status: 'OPERATIONAL', color: 'text-osin-emerald' },
                { label: 'Graph Intelligence', status: 'SYNCED', color: 'text-osin-emerald' },
                { label: 'Safety Monitor', status: 'ENGAGED', color: 'text-yellow-500' },
                { label: 'Autonomous Mode', status: 'GOD_MODE', color: 'text-osin-purple' },
              ].map((item) => (
                <div key={item.label} className="flex justify-between items-center group">
                  <span className="text-[10px] text-gray-500 group-hover:text-gray-300 transition-colors uppercase font-light">{item.label}</span>
                  <span className={`${item.color} text-[10px] font-bold uppercase tracking-tight`}>{item.status}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Terminal */}
          <div className="flex-1 min-h-0">
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
