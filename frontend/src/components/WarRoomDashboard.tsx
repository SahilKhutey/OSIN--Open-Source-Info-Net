import React, { useState, useEffect } from 'react';

export const WarRoomDashboard: React.FC = () => {
  const [events, setEvents] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);

  useEffect(() => {
    console.log("OSIN: War Room Dashboard initialized. Connecting to secure WebSocket...");
    // Mock WebSocket simulation
    const interval = setInterval(() => {
      setEvents(prev => [{id: Date.now(), title: 'Emergent Signal Detected', credibility_score: 0.85}, ...prev.slice(0, 10)]);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="osin-war-room bg-black text-green-500 p-4 font-mono">
      <header className="border-b border-green-900 pb-2 mb-4 flex justify-between">
        <h1 className="text-2xl font-bold">OSIN TACTICAL HUB [ALPHA-1]</h1>
        <div className="status">ZULU TIME: {new Date().toUTCString()}</div>
      </header>
      
      <div className="grid grid-cols-3 gap-4 h-[80vh]">
        <div className="col-span-2 border border-green-900 p-4 relative">
          <h2 className="text-xl mb-2">GLOBAL SITUATION MAP</h2>
          <div className="w-full h-full bg-green-950/20 flex items-center justify-center border border-green-900/50">
             [HEATMAP_CORE_ACTIVE]
          </div>
        </div>
        
        <div className="border border-green-900 p-4">
          <h2 className="text-xl mb-2">CRITICAL ALERTS</h2>
          <div className="alert-list space-y-2">
            {events.map(e => (
              <div key={e.id} className="p-2 border border-red-900 bg-red-950/20 text-red-500">
                [HIGH_CREDIBILITY] {e.title} ({Math.round(e.credibility_score * 100)}%)
              </div>
            ))}
          </div>
        </div>
      </div>
      
      <footer className="mt-4 border-t border-green-900 pt-2 text-xs flex justify-between">
        <div>SECURITY_LEVEL: ALPHA-1</div>
        <div>ENCRYPTION: AES-256-GCM</div>
      </footer>
    </div>
  );
};
