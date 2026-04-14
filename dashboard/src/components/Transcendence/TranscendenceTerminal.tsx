import React, { useState, useEffect, useRef } from 'react';
import { TerminalLog } from '../../types/transcendence';

const TranscendenceTerminal: React.FC = () => {
  const [logs, setLogs] = useState<TerminalLog[]>([
    { timestamp: new Date().toLocaleTimeString(), message: 'OSIN Transcendence v8.0.0 Boot Sequence Initiated...', type: 'system' },
    { timestamp: new Date().toLocaleTimeString(), message: 'Consciousness Core: ACTIVE', type: 'success' },
    { timestamp: new Date().toLocaleTimeString(), message: 'Strategic Goal Engine: ONLINE', type: 'info' },
  ]);
  const [input, setInput] = useState('');
  const terminalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [logs]);

  const handleCommand = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const newLog: TerminalLog = {
      timestamp: new Date().toLocaleTimeString(),
      message: `> ${input}`,
      type: 'info',
    };

    setLogs((prev) => [...prev, newLog]);
    setInput('');

    // Simulate system response
    setTimeout(() => {
      const response: TerminalLog = {
        timestamp: new Date().toLocaleTimeString(),
        message: `Command "${input}" ingested. Processing strategic vectors...`,
        type: 'system',
      };
      setLogs((prev) => [...prev, response]);
    }, 500);
  };

  const getLogColor = (type: string) => {
    switch (type) {
      case 'success': return 'text-osin-emerald';
      case 'error': return 'text-red-500';
      case 'warn': return 'text-yellow-500';
      case 'system': return 'text-osin-cyan';
      default: return 'text-gray-300';
    }
  };

  return (
    <div className="flex flex-col h-full bg-black/60 backdrop-blur-md border border-gray-800 rounded-xl overflow-hidden font-mono text-sm">
      <div className="bg-gray-900/80 px-4 py-2 border-b border-gray-800 flex justify-between items-center">
        <span className="text-gray-400 text-xs font-orbitron">TRANSCENDENCE_TERMINAL</span>
        <div className="flex space-x-2">
          <div className="w-2 h-2 rounded-full bg-red-900 border border-red-500" />
          <div className="w-2 h-2 rounded-full bg-yellow-900 border border-yellow-500" />
          <div className="w-2 h-2 rounded-full bg-green-900 border border-green-500" />
        </div>
      </div>
      
      <div 
        ref={terminalRef}
        className="flex-1 p-4 overflow-y-auto space-y-1 scrollbar-thin scrollbar-thumb-gray-800 scrollbar-track-transparent"
      >
        {logs.map((log, i) => (
          <div key={i} className="flex space-x-2 animate-in fade-in slide-in-from-left-2 duration-300">
            <span className="text-gray-600 shrink-0">[{log.timestamp}]</span>
            <span className={`${getLogColor(log.type)} break-all`}>{log.message}</span>
          </div>
        ))}
        <div className="flex items-center space-x-2 text-osin-emerald pt-2">
          <span className="animate-pulse">❯</span>
          <form onSubmit={handleCommand} className="flex-1">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="w-full bg-transparent border-none outline-none text-osin-emerald placeholder:text-gray-700"
              placeholder="Awaiting command..."
              autoFocus
            />
          </form>
        </div>
      </div>
    </div>
  );
};

export default TranscendenceTerminal;
