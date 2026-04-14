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
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'analytics' | 'command' | 'satellite' | 'geointel' | 'advanced' | 'autonomous' | 'transcendence' | 'xr'>('transcendence');
  const [users, setUsers] = useState<any[]>([]);
  const [voiceStatus, setVoiceStatus] = useState('ready');
  
  const haptic = useHaptic();
  const { askAgent } = useLLMAgent();

  // Initialize WebSocket with fallback to sample data
  useWebSocket('ws://localhost:8000/ws/intelligence');

  const handleVoiceCommand = async (command: any) => {
    console.log('Voice Command Received:', command.text);
    haptic.onTaskComplete(); // Confirmation pulse

    try {
      const result = await askAgent(command.text);
      
      // Execute multi-sensory feedback and actions
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
      case 'SHOW_THREATS':
        haptic.onThreatDetected();
        break;
      case 'ANALYZE_NODE':
        haptic.onNodeSelect();
        break;
      case 'ZOOM_EARTH':
        haptic.feedback('medium');
        break;
      default:
        haptic.feedback('light');
    }
  };

  return (
    <div className="min-h-screen bg-black text-green-400 font-mono">
      <header className="bg-gray-900 border-b border-green-500 p-4 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold text-blue-400">OSIN GEO-INTELLIGENCE</h1>
          <nav className="flex gap-2">
            <button 
              className={`px-4 py-2 rounded transition-colors ${
                activeTab === 'dashboard' 
                  ? 'bg-green-900 text-white border border-green-400' 
                  : 'hover:bg-gray-800 border border-gray-700'
              }`}
              onClick={() => setActiveTab('dashboard')}
            >
              3D Dashboard
            </button>
            <button 
              className={`px-4 py-2 rounded transition-colors ${
                activeTab === 'analytics' 
                  ? 'bg-green-900 text-white border border-green-400' 
                  : 'hover:bg-gray-800 border border-gray-700'
              }`}
              onClick={() => setActiveTab('analytics')}
            >
              Analytics
            </button>
            <button 
              className={`px-4 py-2 rounded transition-colors ${
                activeTab === 'command' 
                  ? 'bg-blue-900 text-white border border-blue-400' 
                  : 'hover:bg-gray-800 border border-gray-700 text-blue-400 border-blue-900/40'
              }`}
              onClick={() => setActiveTab('command')}
            >
              🚀 Command Center
            </button>
            <button 
              className={`px-4 py-2 rounded transition-colors ${
                activeTab === 'satellite' 
                  ? 'bg-indigo-900 text-white border border-indigo-400' 
                  : 'hover:bg-gray-800 border border-gray-700 text-indigo-400 border-indigo-900/40'
              }`}
              onClick={() => setActiveTab('satellite')}
            >
              🛰️ Satellite Ops
            </button>
            <button 
              className={`px-4 py-2 rounded transition-colors ${
                activeTab === 'geointel' 
                  ? 'bg-emerald-900 text-white border border-emerald-400' 
                  : 'hover:bg-gray-800 border border-gray-700 text-emerald-400 border-emerald-900/40'
              }`}
              onClick={() => setActiveTab('geointel')}
            >
              📍 Geo-Intelligence
            </button>
            <button 
              className={`px-4 py-2 rounded transition-colors ${
                activeTab === 'advanced' 
                  ? 'bg-purple-900 text-white border border-purple-400' 
                  : 'hover:bg-gray-800 border border-gray-700 text-purple-400 border-purple-900/40'
              }`}
              onClick={() => setActiveTab('advanced')}
            >
              ⏳ Time-Travel Command
            </button>
            <button 
              className={`px-4 py-2 rounded transition-colors ${
                activeTab === 'transcendence' 
                  ? 'bg-osin-emerald text-black border border-osin-emerald shadow-[0_0_15px_rgba(16,185,129,0.4)]' 
                  : 'hover:bg-gray-800 border border-gray-700 text-osin-emerald border-osin-emerald/20'
              }`}
              onClick={() => setActiveTab('transcendence')}
            >
              🌌 Transcendence
            </button>
            <button 
              className={`px-4 py-2 rounded transition-colors ${
                activeTab === 'xr' 
                  ? 'bg-cyan-900 text-white border border-cyan-400 shadow-[0_0_20px_rgba(6,182,212,0.5)]' 
                  : 'hover:bg-gray-800 border border-gray-700 text-cyan-400 border-cyan-900/40'
              }`}
              onClick={() => setActiveTab('xr')}
            >
              🖐️ XR Command
            </button>
          </nav>
        </div>
      </header>
      
      <main className={(activeTab === 'command' || activeTab === 'satellite' || activeTab === 'geointel' || activeTab === 'advanced' || activeTab === 'autonomous' || activeTab === 'xr') ? '' : 'p-4'}>
        <div className={(activeTab === 'command' || activeTab === 'satellite' || activeTab === 'geointel' || activeTab === 'advanced' || activeTab === 'autonomous' || activeTab === 'xr') ? 'w-full h-[calc(100vh-73px)]' : 'max-w-7xl mx-auto'}>
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
              <>
                <XREnvironment />
                <VoiceController 
                  onCommand={handleVoiceCommand} 
                  onStatusChange={setVoiceStatus} 
                />
                <MultiplayerController 
                  onUsersUpdate={setUsers} 
                  onUserJoin={(u) => console.log('MP: Joining', u.name)}
                  onUserLeave={(id) => console.log('MP: Leaving', id)}
                />
                <PerformanceOptimizer maxNodes={400} />
                
                {/* Collaborative Avatars */}
                {users.map(u => (
                  <UserAvatar key={u.id} user={u} />
                ))}

                {/* Immersive HUD Overlay */}
                <div className="absolute top-20 right-6 flex flex-col gap-2 pointer-events-none z-[60]">
                  <div className="bg-black/60 backdrop-blur-md border border-cyan-500/30 px-3 py-1 rounded text-[10px] uppercase flex items-center gap-2">
                      <span className={`w-1.5 h-1.5 rounded-full ${voiceStatus === 'listening' ? 'bg-red-500 animate-pulse' : 'bg-cyan-500'}`}></span>
                      SENSOR: {voiceStatus}
                  </div>
                  <div className="bg-black/60 backdrop-blur-md border border-cyan-500/30 px-3 py-1 rounded text-[10px] uppercase flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-green-500"></span>
                      ACTIVE ANALYSTS: {users.length}
                  </div>
                </div>
              </>
            )}
          </Suspense>
        </div>
      </main>


      {/* Floating XR Toggle Button for immersive switching */}
      {activeTab !== 'xr' && (
        <button 
            onClick={() => setActiveTab('xr')}
            className="fixed bottom-8 right-8 bg-cyan-600 hover:bg-cyan-500 text-white p-4 rounded-full shadow-2xl hover:scale-110 transition-all z-[100] group flex items-center gap-2"
        >
            <span className="hidden group-hover:block font-bold text-xs tracking-tighter">LAUNCH XR</span>
            <span className="text-xl">🖐️</span>
        </button>
      )}

      
      {(activeTab !== 'command' && activeTab !== 'satellite' && activeTab !== 'geointel' && activeTab !== 'advanced' && activeTab !== 'transcendence') && (
        <footer className="bg-gray-900 border-t border-green-500 p-4 text-center text-sm text-gray-500 mt-8">
          <p>OSIN Geo-Intelligence System • Real-time Global Monitoring • Advanced 3D Analytics</p>
        </footer>
      )}
    </div>
  );
}

export default App;
