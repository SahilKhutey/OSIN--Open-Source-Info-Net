import React, { useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Terminal as TerminalIcon, Shield } from 'lucide-react';

interface TerminalProps {
  output: string[];
}

const Terminal: React.FC<TerminalProps> = ({ output }) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [output]);

  return (
    <div className="flex flex-col h-full bg-black/40 p-4 border border-white/5 rounded-lg backdrop-blur-sm">
      <div className="flex justify-between items-center mb-3">
        <div className="flex items-center gap-2 text-green-500">
          <TerminalIcon size={14} />
          <h2 className="text-[10px] font-bold tracking-[0.2em] uppercase">Operations Terminal</h2>
        </div>
        <div className="flex items-center gap-4 opacity-30 text-[9px] uppercase tracking-widest text-green-500">
          <span>Encrypted Session</span>
          <Shield size={10} />
        </div>
      </div>
      
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto font-mono text-[11px] leading-relaxed pr-2 custom-scrollbar"
      >
        <div className="space-y-1">
          {output.map((line, index) => (
            <motion.div
              key={`${index}-${line}`}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex gap-3"
            >
              <span className="text-green-800">[{new Date().toLocaleTimeString('en-GB')}]</span>
              <span className={line.includes('alert') ? 'text-rose-400' : 'text-green-500/80'}>
                {line}
              </span>
            </motion.div>
          ))}
        </div>
        <div className="flex items-center mt-2">
          <span className="text-green-500 mr-2 opacity-50">{'>'}</span>
          <div className="w-1.5 h-3.5 bg-green-500 animate-[pulse_1s_infinite] shadow-[0_0_8px_rgba(34,197,94,0.5)]"></div>
        </div>
      </div>
      
      <style>{`
        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(34,197,94,0.1); border-radius: 10px; }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: rgba(34,197,94,0.2); }
      `}</style>
    </div>
  );
};

export default Terminal;
