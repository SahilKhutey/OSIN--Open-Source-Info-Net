import React from 'react';
import './App.css';
import SignalHUD from './components/SignalHUD';
import CorrelationGraph from './components/CorrelationGraph';
import { Shield, Radio, Crosshair, Zap } from 'lucide-react';

function App() {
  return (
    <div className="aoie-dashboard bg-black h-screen w-screen flex flex-col overflow-hidden text-green-500 selection:bg-green-500 selection:text-black">
      {/* Header Bar */}
      <header className="h-14 border-b border-green-900 bg-green-950/20 flex items-center justify-between px-6 z-10">
        <div className="flex items-center gap-3">
          <div className="bg-green-500 p-1 rounded">
            <Radio className="text-black" size={20} />
          </div>
          <div>
            <h1 className="text-lg font-black tracking-tighter uppercase">AOIE // ADVANCED OSINT ENGINE</h1>
            <p className="text-[10px] opacity-60 tracking-[0.2em]">STRATEGIC_CORRELATION_HUB_V3.0</p>
          </div>
        </div>
        
        <div className="flex items-center gap-6">
          <div className="flex gap-4 text-[10px] items-center">
            <span className="flex items-center gap-1"><Shield size={12} /> SECURE_CONNECTION: AES-256</span>
            <span className="flex items-center gap-1 text-green-400"><Zap size={12} /> ENGINE_STATUS: NOMINAL</span>
          </div>
          <button className="bg-green-900/40 border border-green-700 hover:bg-green-500 hover:text-black transition-all px-4 py-1 text-xs uppercase font-bold tracking-widest rounded">
            Emergency Wipe
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 flex w-full relative">
        {/* Left Side: Correlation Map */}
        <section className="flex-1 p-6 relative">
          <div className="absolute top-8 left-8 z-10 flex flex-col gap-2">
            <div className="bg-black/60 backdrop-blur-md border border-green-900 p-4 rounded-lg shadow-2xl">
              <div className="flex items-center gap-2 mb-2 text-xs font-bold text-green-400">
                <Crosshair size={14} /> ACTIVE_TARGETS: 242
              </div>
              <div className="h-[2px] w-32 bg-green-900 mb-2">
                <div className="h-full w-2/3 bg-green-500"></div>
              </div>
              <p className="text-[9px] opacity-50 uppercase">Analysis Confidence: 94%</p>
            </div>
          </div>
          <CorrelationGraph />
        </section>

        {/* Right Side: Signal HUD */}
        <aside className="w-80 h-full">
          <SignalHUD />
        </aside>
      </main>

      {/* Footer Bar */}
      <footer className="h-8 border-t border-green-900 bg-black flex items-center justify-between px-6 text-[9px] opacity-40 font-mono tracking-widest">
        <span>&copy; OSIG_GLOBAL_INTELLIGENCE_GRID // 2026</span>
        <div className="flex gap-4">
          <span>COOR_X: 34.0522</span>
          <span>COOR_Y: -118.2437</span>
          <span>SYSTEM_UPTIME: 99.999%</span>
        </div>
      </footer>
    </div>
  );
}

export default App;
