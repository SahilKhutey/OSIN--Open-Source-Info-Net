import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, Shield, AlertTriangle, Globe } from 'lucide-react';

interface Signal {
  id: string;
  source: string;
  content: string;
  timestamp: string;
  type: 'social' | 'news' | 'financial' | 'web';
  score: number;
}

const SignalHUD: React.FC = () => {
  const [signals, setSignals] = useState<Signal[]>([]);

  useEffect(() => {
    // Simulated real-time signal stream
    const interval = setInterval(() => {
      const newSignal: Signal = {
        id: Math.random().toString(36).substr(2, 9),
        source: ['Twitter', 'Reuters', 'GDELT', 'Reddit', 'Bloomberg'][Math.floor(Math.random() * 5)],
        content: `Intelligence signal detected: ${['Satellite shift', 'Market anomaly', 'Narrative propagation', 'Node heartbeat'][Math.floor(Math.random() * 4)]} in sector ${Math.floor(Math.random() * 100)}`,
        timestamp: new Date().toLocaleTimeString(),
        type: ['social', 'news', 'financial', 'web'][Math.floor(Math.random() * 4)] as any,
        score: Math.random()
      };
      setSignals(prev => [newSignal, ...prev].slice(0, 10));
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="signal-hud bg-black border-l border-green-900 h-full p-4 font-mono text-green-500 overflow-hidden">
      <div className="flex items-center gap-2 mb-4 border-b border-green-800 pb-2">
        <Activity className="animate-pulse" size={20} />
        <h2 className="text-sm font-bold tracking-widest uppercase">Live Signal Stream</h2>
      </div>

      <div className="space-y-4">
        <AnimatePresence>
          {signals.map((signal) => (
            <motion.div
              key={signal.id}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="signal-card border border-green-900 p-2 text-xs bg-green-950/20 rounded shadow-sm hover:bg-green-900/30 transition-colors"
            >
              <div className="flex justify-between mb-1">
                <span className="font-bold flex items-center gap-1">
                  <Globe size={12} /> {signal.source}
                </span>
                <span className="opacity-50">{signal.timestamp}</span>
              </div>
              <p className="mb-2 italic">"{signal.content}"</p>
              <div className="flex items-center justify-between">
                <div className="flex gap-2">
                  <span className="px-1 bg-green-900/50 rounded uppercase text-[10px]">{signal.type}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Shield size={10} className={signal.score > 0.8 ? "text-green-400" : "text-yellow-600"} />
                  <span className="text-[10px]">CORR: {(signal.score * 100).toFixed(0)}%</span>
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      <div className="absolute bottom-4 left-4 right-4 text-[10px] opacity-40 flex justify-between">
        <span>GRID_STATUS: ACTIVE</span>
        <span>LATENCY: 42ms</span>
      </div>
    </div>
  );
};

export default SignalHUD;
