import React, { useState } from 'react';
import { Dashboard } from './components/Dashboard';
import { EnhancedAnalytics } from './components/EnhancedAnalytics';
import { useWebSocket } from './hooks/useWebSocket';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'analytics'>('dashboard');
  
  // Initialize WebSocket with fallback to sample data
  useWebSocket('ws://localhost:8000/ws/intelligence');

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
          </nav>
        </div>
      </header>
      
      <main className="p-4">
        <div className="max-w-7xl mx-auto">
          {activeTab === 'dashboard' ? <Dashboard /> : <EnhancedAnalytics />}
        </div>
      </main>
      
      <footer className="bg-gray-900 border-t border-green-500 p-4 text-center text-sm text-gray-500 mt-8">
        <p>OSIN Geo-Intelligence System • Real-time Global Monitoring • Advanced 3D Analytics</p>
      </footer>
    </div>
  );
}

export default App;
