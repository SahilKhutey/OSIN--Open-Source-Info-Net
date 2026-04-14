import React from 'react';
import { motion } from 'framer-motion';
import { ConsciousnessState } from '../../types/transcendence';

interface Props {
  state: ConsciousnessState;
}

const CognitiveMetrics: React.FC<Props> = ({ state }) => {
  const metrics = [
    { label: 'Confidence', value: state.confidence, color: 'bg-osin-emerald' },
    { label: 'Uncertainty', value: state.uncertainty, color: 'bg-yellow-500' },
    { label: 'Strategic Focus', value: state.strategicFocus, color: 'bg-osin-cyan' },
    { label: 'Cognitive Load', value: state.cognitiveLoad, color: 'bg-osin-purple' },
  ];

  return (
    <div className="grid grid-cols-1 gap-6">
      {metrics.map((metric) => (
        <div key={metric.label}>
          <div className="flex justify-between text-xs font-orbitron text-gray-400 mb-2 uppercase tracking-tighter">
            <span>{metric.label}</span>
            <span className="text-osin-cyan">{(metric.value * 100).toFixed(1)}%</span>
          </div>
          <div className="h-2 w-full bg-gray-900/50 rounded-full border border-gray-800 p-[1px] overflow-hidden">
            <motion.div
              className={`h-full rounded-full ${metric.color} shadow-[0_0_10px_rgba(34,211,238,0.3)]`}
              initial={{ width: 0 }}
              animate={{ width: `${metric.value * 100}%` }}
              transition={{ duration: 1, ease: 'easeOut' }}
            />
          </div>
        </div>
      ))}
    </div>
  );
};

export default CognitiveMetrics;
