import React from 'react';
import { motion } from 'framer-motion';
import { Alert } from '../../types/command_center';

interface ThreatFeedProps {
  alerts: Alert[];
  onAlertClick: (alert: Alert) => void;
}

const ThreatFeed: React.FC<ThreatFeedProps> = ({ alerts, onAlertClick }) => {
  const getColorClasses = (level: string) => {
    switch (level) {
      case 'CRITICAL': return 'text-red-400 border-red-500/50 bg-red-950/10';
      case 'HIGH': return 'text-orange-400 border-orange-500/50 bg-orange-950/10';
      case 'MEDIUM': return 'text-yellow-400 border-yellow-500/50 bg-yellow-950/10';
      case 'LOW': return 'text-green-400 border-green-500/50 bg-green-950/10';
      default: return 'text-gray-400 border-gray-500/50 bg-gray-900/10';
    }
  };

  return (
    <div className="flex flex-col h-full">
      <h2 className="text-red-500 text-sm font-bold tracking-widest mb-4 flex items-center gap-2">
        <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
        LIVE THREAT FEED
      </h2>
      <div className="space-y-3 overflow-y-auto pr-2 custom-scrollbar" style={{ maxHeight: 'calc(100vh - 400px)' }}>
        {alerts.map((alert, index) => (
          <motion.div
            key={alert.id}
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
            className={`border rounded-lg p-3 cursor-pointer hover:scale-[1.02] transition-transform duration-200 border-l-4 ${getColorClasses(alert.level)}`}
            onClick={() => onAlertClick(alert)}
          >
            <div className="flex justify-between items-start mb-1">
              <span className="font-bold text-[10px] tracking-tighter px-1.5 py-0.5 rounded bg-black/40">
                {alert.level}
              </span>
              <span className="text-[10px] opacity-60 font-mono">
                {alert.timestamp.toLocaleTimeString()}
              </span>
            </div>
            <p className="text-xs leading-relaxed font-medium mb-2">{alert.message}</p>
            <div className="flex justify-between items-center pt-2 border-t border-white/5 mt-1">
              <span className="text-[10px] opacity-50 uppercase tracking-widest">{alert.source}</span>
              <span className="text-[10px] font-mono text-white/40">
                {Math.round(alert.confidence * 100)}% CONF
              </span>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default ThreatFeed;
