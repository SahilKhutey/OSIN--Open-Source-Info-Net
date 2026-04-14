import React, { useState, Suspense } from 'react';
import HexGridLoading from './components/common/HexGridLoading';
import { Dashboard } from './components/Dashboard';
import { EnhancedAnalytics } from './components/EnhancedAnalytics';
import OSINCommandCenter from './components/CommandCenter/OSINCommandCenter';
import SatelliteCommandCenter from './components/CommandCenter/SatelliteCommandCenter';
import GeoIntelligenceCommandCenter from './components/CommandCenter/GeoIntelligenceCommandCenter';
import AdvancedCommandCenter from './components/CommandCenter/AdvancedCommandCenter';
import AutonomousCommandCenter from './components/CommandCenter/AutonomousCommandCenter';
import TranscendenceDashboard from './components/Transcendence/TranscendenceDashboard';
import { XREnvironment } from './xr/XREnvironment';
import { VoiceController } from './voice/VoiceController';
import { MultiplayerController } from './multiplayer/MultiplayerController';
import { UserAvatar } from './multiplayer/UserAvatar';
import { PerformanceOptimizer } from './performance/PerformanceOptimizer';
import { useHaptic } from './haptic/HapticController';
import { useLLMAgent } from './llm/LLMAgent';
import { useWebSocket } from './hooks/useWebSocket';
import { motion, AnimatePresence } from 'framer-motion';
import './App.css';

type TabType = 'dashboard' | 'analytics' | 'command' | 'satellite' | 'geointel' | 'advanced' | 'autonomous' | 'transcendence' | 'xr';

function App() {
  const [activeTab, setActiveTab] = useState<TabType>('transcendence');
  const [users, setUsers] = useState<any[]>([]);
  const [voiceStatus, setVoiceStatus] = useState('ready');
  
  const haptic = useHaptic();
  const { askAgent } = useLLMAgent();

  // Initialize WebSocket with fallback to sample data
  useWebSocket('ws://localhost:8000/ws/intelligence');

  const handleVoiceCommand = async (command: any) => {
    console.log('Voice Command Received:', command.text);
    haptic.onTaskComplete();

    try {
      const result = await askAgent(command.text);
      if (result.actions) {
        result.actions.forEach((action: string) => {
          processAction(action, result.parameters);
        });
      }
    } catch (err) {
      console.error('AI Command Processing Failed:', err);
      haptic.onCriticalWarning();
    }
  };

  const processAction = (action: string, params: any) => {
    console.log(`OSIN Executive: Executing ${action}`, params);
    switch (action) {
      case 'SHOW_THREATS': haptic.onThreatDetected(); break;
      case 'ANALYZE_NODE': haptic.onNodeSelect(); break;
      case 'ZOOM_EARTH': haptic.feedback('medium'); break;
      default: haptic.feedback('light');
    }
  };

  const navItems: { id: TabType; label: string; icon: string; color: string }[] = [
    { id: 'transcendence', label: 'Transcendence', icon: '🌌', color: 'emerald' },
    { id: 'dashboard', label: 'Analytics Hub', icon: '📊', color: 'blue' },
    { id: 'xr', label: 'XR Command', icon: '🖐️', color: 'cyan' },
    { id: 'command', label: 'Command Ctr', icon: '🚀', color: 'blue' },
    { id: 'satellite', label: 'Satellite Ops', icon: '🛰️', color: 'indigo' },
    { id: 'geointel', label: 'Geo-Intel', icon: '📍', color: 'emerald' },
    { id: 'advanced', label: 'Temporal Ops', icon: '⏳', color: 'purple' },
  ];

  return (
    <div className="flex h-screen w-screen bg-[#020408] text-white overflow-hidden">
      
      {/* STRATEGIC SIDEBAR - Fixed proportions */}
      <aside className="w-20 lg:w-64 flex flex-col bg-black/40 backdrop-blur-3xl border-r border-white/5 z-[100] transition-all duration-500 overflow-hidden">
        <div className="p-6">
          <div className="flex items-center gap-3 mb-10">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-osin-emerald to-osin-cyan flex items-center justify-center shadow-[0_0_20px_rgba(16,185,129,0.3)] animate-flicker">
                <span className="text-xl">O</span>
            </div>
            <div className="hidden lg:block">
                <h1 className="text-lg font-black tracking-tighter text-white font-tactical">OSIN COMMAND</h1>
                <p className="text-[9px] text-osin-emerald opacity-60 tracking-widest uppercase font-mono">Core Node 8.0</p>
            </div>
          </div>

          <nav className="space-y-2">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => {
                    setActiveTab(item.id);
                    haptic.feedback('light');
                }}
                className={`w-full group relative flex items-center gap-4 px-4 py-3 rounded-xl transition-all duration-300 ${
                  activeTab === item.id 
                    ? `bg-osin-${item.color}/10 border border-osin-${item.color}/30 text-osin-${item.color} shadow-[0_0_20px_rgba(255,255,255,0.02)]`
                    : 'hover:bg-white/5 border border-transparent text-gray-500 hover:text-gray-300'
                }`}
              >
                <span className="text-xl opacity-80 group-hover:scale-110 transition-transform">{item.icon}</span>
                <span className="hidden lg:block font-tactical text-[11px] font-bold tracking-widest whitespace-nowrap">{item.label}</span>
                {activeTab === item.id && (
                    <motion.div 
                        layoutId="activeTabIndicator"
                        className={`absolute left-0 w-1 h-1/2 bg-osin-${item.color} rounded-full`}
                    />
                )}
              </button>
            ))}
          </nav>
        </div>

        <div className="mt-auto p-6 space-y-4">
            <div className="hidden lg:block bg-white/5 rounded-xl p-4 border border-white/5">
                <div className="flex justify-between items-center mb-2">
                    <span className="text-[10px] text-gray-500 uppercase font-tactical">System Load</span>
                    <span className="text-[10px] text-osin-emerald font-bold uppercase font-tactical">Optimal</span>
                </div>
                <div className="h-1 w-full bg-white/10 rounded-full overflow-hidden">
                    <div className="h-full w-2/3 bg-osin-emerald shadow-[0_0_10px_#10b981]" />
                </div>
            </div>
            
            <button 
                onClick={() => window.location.reload()}
                className="w-full flex items-center justify-center gap-2 py-3 bg-red-500/5 hover:bg-red-500/10 border border-red-500/20 text-red-500 rounded-xl transition-all group"
            >
                <span className="text-xs group-hover:rotate-180 transition-transform duration-500">🔄</span>
                <span className="hidden lg:block text-[9px] font-black tracking-[0.2em] font-tactical">HARD RELOAD</span>
            </button>
        </div>
      </aside>

      {/* MAIN INTELLIGENCE HUB */}
      <main className="flex-1 relative flex flex-col min-w-0 bg-[radial-gradient(circle_at_50%_0%,_#111827_0%,_transparent_50%)]">
        
        {/* UPPER HUD - Status bar */}
        <header className="h-20 flex items-center justify-between px-10 border-b border-white/5 backdrop-blur-md z-40">
            <div className="flex items-center gap-10">
                <div className="flex items-center gap-3">
                    <span className="text-xs text-gray-500 font-tactical uppercase">Operation:</span>
                    <span className="text-xs text-osin-cyan font-black font-tactical tracking-widest uppercase">
                        {navItems.find(i => i.id === activeTab)?.label}
                    </span>
                </div>
                <div className="hidden xl:flex items-center gap-6 opacity-40">
                   <div className="h-4 w-px bg-white/20" />
                   <div className="flex items-center gap-3">
                        <span className="text-[10px] text-gray-500 font-tactical">SEC_LEVEL:</span>
                        <span className="text-[10px] text-white font-bold font-mono">P0-V8</span>
                   </div>
                   <div className="flex items-center gap-3">
                        <span className="text-[10px] text-gray-500 font-tactical">GEO_NODE:</span>
                        <span className="text-[10px] text-white font-bold font-mono">GLOBAL.OSIN.001</span>
                   </div>
                </div>
            </div>

            <div className="flex items-center gap-6">
                <div className="flex -space-x-3">
                    {users.slice(0, 3).map((u, i) => (
                        <div key={i} className="w-8 h-8 rounded-full border-2 border-black bg-gray-800 flex items-center justify-center text-[10px] font-bold shadow-xl">
                            {u.name[0]}
                        </div>
                    ))}
                    {users.length > 3 && (
                        <div className="w-8 h-8 rounded-full border-2 border-black bg-osin-emerald text-black flex items-center justify-center text-[10px] font-black shadow-xl">
                            +{users.length - 3}
                        </div>
                    )}
                </div>
                <div className="h-8 w-px bg-white/10" />
                <div className={`px-4 py-2 border rounded-lg flex items-center gap-3 transition-colors ${voiceStatus === 'listening' ? 'border-red-500/50 bg-red-500/10' : 'border-white/10 bg-white/5'}`}>
                    <span className={`w-2 h-2 rounded-full ${voiceStatus === 'listening' ? 'bg-red-500 animate-pulse' : 'bg-osin-emerald'}`} />
                    <span className="text-[10px] font-tactical font-bold uppercase tracking-widest">Acoustic: {voiceStatus}</span>
                </div>
            </div>
        </header>

        {/* CONTENT VIEWPORT */}
        <div className="flex-1 overflow-auto tactical-scroll relative">
            <AnimatePresence mode="wait">
                <motion.div
                    key={activeTab}
                    initial={{ opacity: 0, scale: 0.99, y: 10 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 1.01, y: -10 }}
                    transition={{ duration: 0.4, ease: "circOut" }}
                    className="h-full w-full"
                >
                    <Suspense fallback={<HexGridLoading />}>
                        {activeTab === 'dashboard' && <Dashboard />}
                        {activeTab === 'analytics' && <EnhancedAnalytics />}
                        {activeTab === 'command' && <OSINCommandCenter />}
                        {activeTab === 'satellite' && <SatelliteCommandCenter />}
                        {activeTab === 'geointel' && <GeoIntelligenceCommandCenter />}
                        {activeTab === 'advanced' && <AdvancedCommandCenter />}
                        {activeTab === 'autonomous' && <AutonomousCommandCenter />}
                        {activeTab === 'transcendence' && <TranscendenceDashboard />}
                        {activeTab === 'xr' && (
                            <XREnvironment>
                                <MultiplayerController 
                                    onUsersUpdate={setUsers} 
                                    onUserJoin={(u) => console.log('MP: Joining', u.name)}
                                    onUserLeave={(id) => console.log('MP: Leaving', id)}
                                />
                                <PerformanceOptimizer maxNodes={400} />
                                {users.map(u => <UserAvatar key={u.id} user={u} />)}
                            </XREnvironment>
                        )}
                    </Suspense>
                </motion.div>
            </AnimatePresence>
            
            {/* INLINE CONTROLLERS */}
            {activeTab === 'xr' && (
                <VoiceController onCommand={handleVoiceCommand} onStatusChange={setVoiceStatus} />
            )}
        </div>

        {/* DATA GLOW OVERLAY */}
        <div className="absolute inset-x-0 bottom-0 h-64 bg-gradient-to-t from-osin-emerald/5 to-transparent pointer-events-none" />
      </main>
    </div>
  );
}

export default App;
