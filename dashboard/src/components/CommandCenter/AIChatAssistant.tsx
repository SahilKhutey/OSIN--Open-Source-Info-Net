import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { MessageSquare, Send, X, Bot, User, Sparkles } from 'lucide-react';

interface AIChatAssistantProps {
  onClose: () => void;
}

const AIChatAssistant: React.FC<AIChatAssistantProps> = ({ onClose }) => {
  const [messages, setMessages] = useState([
    { role: 'ai', content: 'OSIN STRATEGIC ANALYST ONLINE. SPRECTRUM ANALYSIS ACTIVE. HOW CAN I ASSIST IN YOUR MISSION?' }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const handleSend = () => {
    if (!input.trim()) return;
    
    const userMsg = input.trim();
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setInput('');
    setIsTyping(true);
    
    // Simulate AI response with strategic depth
    setTimeout(() => {
      setIsTyping(false);
      setMessages(prev => [...prev, { 
        role: 'ai', 
        content: `ANALYSIS COMPLETE. CROSS-SIGNAL CORRELATION INDICATES ${Math.floor(Math.random() * 8) + 2} EMERGING THREAT VECTORS IN THE SELECTED QUADRANT. RECOMMEND DEPLOYING AUTONOMOUS SWARM REPLICATION FOR ENHANCED COVERAGE.` 
      }]);
    }, 1500);
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95, y: 20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95, y: 20 }}
      className="fixed bottom-24 right-8 w-[400px] bg-black/90 border border-blue-500/30 rounded-2xl shadow-[0_20px_50px_rgba(0,149,255,0.15)] z-[60000] backdrop-blur-xl overflow-hidden"
    >
      <div className="flex flex-col h-[500px]">
        {/* Header */}
        <div className="p-4 bg-gradient-to-r from-blue-900/40 to-black border-b border-white/10 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center border border-blue-400/30">
              <Sparkles size={16} className="text-blue-400" />
            </div>
            <div>
              <h3 className="text-xs font-bold text-blue-400 tracking-[0.2em] uppercase">Meta-Analyst v2</h3>
              <div className="flex items-center gap-1">
                <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
                <span className="text-[8px] text-green-500 uppercase tracking-widest font-bold">Synchronized</span>
              </div>
            </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-white/5 rounded-full transition-colors text-gray-500 hover:text-white">
            <X size={18} />
          </button>
        </div>
        
        {/* Messages */}
        <div 
          ref={scrollRef}
          className="flex-1 overflow-y-auto p-4 space-y-4 font-mono text-[11px] custom-scrollbar"
        >
          {messages.map((msg, index) => (
            <div key={index} className={`flex ${msg.role === 'ai' ? 'justify-start' : 'justify-end'}`}>
              <div className={`max-w-[85%] flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                <div className={`w-6 h-6 rounded flex items-center justify-center shrink-0 border ${
                  msg.role === 'ai' ? 'bg-blue-900/20 border-blue-500/30 text-blue-400' : 'bg-gray-800/20 border-white/10 text-gray-400'
                }`}>
                  {msg.role === 'ai' ? <Bot size={12} /> : <User size={12} />}
                </div>
                <div className={`p-3 rounded-xl leading-relaxed ${
                  msg.role === 'ai' ? 'bg-blue-500/10 text-blue-100/90' : 'bg-white/5 text-gray-300'
                }`}>
                  {msg.content}
                </div>
              </div>
            </div>
          ))}
          {isTyping && (
            <div className="flex justify-start">
              <div className="bg-blue-500/10 p-3 rounded-xl flex gap-1">
                <span className="w-1 h-1 bg-blue-400 rounded-full animate-bounce" />
                <span className="w-1 h-1 bg-blue-400 rounded-full animate-bounce [animation-delay:0.2s]" />
                <span className="w-1 h-1 bg-blue-400 rounded-full animate-bounce [animation-delay:0.4s]" />
              </div>
            </div>
          )}
        </div>
        
        {/* Input */}
        <div className="p-4 bg-black/50 border-t border-white/5">
          <div className="relative flex items-center">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Query strategic matrix..."
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-xs text-white placeholder:text-white/20 focus:outline-none focus:border-blue-500/50 transition-colors pr-12"
            />
            <button
              onClick={handleSend}
              className="absolute right-2 p-2 bg-blue-600 hover:bg-blue-500 rounded-lg transition-colors text-white"
            >
              <Send size={14} />
            </button>
          </div>
          <p className="text-[7px] text-center mt-3 opacity-20 uppercase tracking-[0.3em]">
            OSIN Advanced Reasoning Core // Encrypted Transmission
          </p>
        </div>
      </div>
    </motion.div>
  );
};

export default AIChatAssistant;
