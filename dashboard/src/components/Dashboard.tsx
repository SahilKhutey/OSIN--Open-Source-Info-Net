import React from 'react';
import { AdvancedGlobe } from './AdvancedGlobe';
import { useStore } from '../store/useStore';
import '../styles/Dashboard.css';

export const Dashboard: React.FC = () => {
  const { events, clusters, heatmap } = useStore();

  const recentEvents = events.slice(0, 10);
  const criticalEvents = events.filter(e => e.severity === 'critical');
  const topSources = Array.from(new Set(events.map(e => e.source)))
    .slice(0, 6)
    .map(source => ({
      source,
      count: events.filter(e => e.source === source).length
    }))
    .sort((a, b) => b.count - a.count);

  return (
    <div className="h-full w-full flex flex-col p-8 tactical-scroll overflow-auto">
      {/* HUD Header */}
      <header className="flex justify-between items-end mb-8 border-b border-white/5 pb-6">
        <div>
           <h1 className="text-3xl font-black font-tactical text-white tracking-widest mb-2">INTELLIGENCE_METRICS</h1>
           <p className="text-[10px] text-gray-500 font-mono uppercase tracking-[0.3em]">Temporal Cluster Logic • Node 8.0.S</p>
        </div>
        
        <div className="flex gap-4">
          <div className="glass-panel px-6 py-3 border-osin-emerald/20">
             <div className="text-[9px] text-gray-500 uppercase font-tactical mb-1">Total_Events</div>
             <div className="text-xl font-black font-mono text-osin-emerald">{events.length}</div>
          </div>
          <div className="glass-panel px-6 py-3 border-osin-cyan/20">
             <div className="text-[9px] text-gray-500 uppercase font-tactical mb-1">Clusters</div>
             <div className="text-xl font-black font-mono text-osin-cyan">{clusters.length}</div>
          </div>
          <div className="glass-panel px-6 py-3 border-red-500/20">
             <div className="text-[9px] text-red-500/50 uppercase font-tactical mb-1">Critical</div>
             <div className="text-xl font-black font-mono text-red-500">{criticalEvents.length}</div>
          </div>
        </div>
      </header>

      {/* STRATEGIC GRID */}
      <div className="flex-1 grid grid-cols-12 gap-6 min-h-0">
        
        {/* PANEL LEFT: Cluster Intelligence (Col-3) */}
        <div className="col-span-12 xl:col-span-3 flex flex-col gap-6">
          <div className="glass-panel flex-1 flex flex-col min-h-[300px]">
            <div className="p-4 border-b border-white/5 flex justify-between items-center">
              <h2 className="text-xs font-bold font-tactical text-osin-cyan">Cluster Analysis</h2>
              <span className="text-[9px] bg-osin-cyan/10 text-osin-cyan px-2 py-0.5 rounded uppercase">{clusters.length}</span>
            </div>
            <div className="p-4 flex-1 overflow-auto tactical-scroll">
              {clusters.length === 0 ? (
                <div className="h-full flex items-center justify-center text-[10px] text-gray-600 uppercase">Idle_Search...</div>
              ) : (
                <div className="space-y-4">
                  {clusters.map((cluster, idx) => (
                    <div key={idx} className="group p-3 bg-white/5 border border-white/5 rounded-xl hover:bg-white/10 transition-colors">
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-[10px] font-bold text-white uppercase">Cluster_{idx + 1}</span>
                        <span className="text-[9px] text-gray-500">{cluster.events.length} E</span>
                      </div>
                      <div className="text-[9px] text-gray-600 font-mono mb-3">POS: {cluster.center.lat.toFixed(2)}, {cluster.center.lng.toFixed(2)}</div>
                      <div className="h-1 w-full bg-white/10 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-gradient-to-r from-osin-cyan to-osin-emerald shadow-[0_0_10px_rgba(34,211,238,0.5)] transition-all duration-1000" 
                          style={{ width: `${(cluster.intensity / 10) * 100}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="glass-panel h-64 flex flex-col">
            <div className="p-4 border-b border-white/5">
              <h2 className="text-xs font-bold font-tactical text-osin-purple">Activity Hotspots</h2>
            </div>
            <div className="p-4 flex-1 overflow-auto tactical-scroll">
                <div className="space-y-2">
                  {heatmap.slice(0, 5).map((h, idx) => (
                    <div key={idx} className="flex justify-between items-center bg-osin-purple/5 p-2 rounded border border-osin-purple/10">
                      <span className="text-[10px] text-osin-purple font-black">{(h.intensity * 100).toFixed(0)}%</span>
                      <span className="text-[9px] text-gray-500 uppercase">{h.events.length} Data Points</span>
                    </div>
                  ))}
                </div>
            </div>
          </div>
        </div>

        {/* PANEL CENTER: Global Visualization (Col-6) */}
        <div className="col-span-12 xl:col-span-6 flex flex-col">
          <div className="glass-panel flex-1 relative overflow-hidden group border-white/10">
            <div className="absolute top-6 left-6 z-10 p-4 bg-black/40 backdrop-blur-md rounded-xl border border-white/10">
               <h2 className="text-lg font-black font-tactical text-osin-emerald mb-1">GLOBAL_INTEL_MAP</h2>
               <div className="flex gap-2">
                  <span className="text-[8px] px-1.5 py-0.5 bg-osin-emerald/10 text-osin-emerald border border-osin-emerald/30 rounded uppercase font-bold">Vector Ingress</span>
                  <span className="text-[8px] px-1.5 py-0.5 bg-oshin-cyan/10 text-osin-cyan border border-osin-cyan/30 rounded uppercase font-bold">Temporal Sync</span>
               </div>
            </div>
            
            <div className="w-full h-full relative cursor-crosshair">
                <AdvancedGlobe />
            </div>

            <div className="absolute bottom-6 right-6 z-10 p-4 bg-black/40 backdrop-blur-md rounded-xl border border-white/10 flex gap-6">
                <div className="text-center">
                    <div className="text-[9px] text-gray-500 uppercase font-tactical mb-1">LATITUDE</div>
                    <div className="text-xs font-bold font-mono">24.551 N</div>
                </div>
                <div className="text-center">
                    <div className="text-[9px] text-gray-500 uppercase font-tactical mb-1">LONGITUDE</div>
                    <div className="text-xs font-bold font-mono">121.15 E</div>
                </div>
            </div>
          </div>
        </div>

        {/* PANEL RIGHT: Signal Log (Col-3) */}
        <div className="col-span-12 xl:col-span-3 flex flex-col gap-6">
          <div className="glass-panel h-48 flex flex-col">
            <div className="p-4 border-b border-white/5">
              <h2 className="text-xs font-bold font-tactical text-white">Ingestion Sources</h2>
            </div>
            <div className="p-4 flex-1 overflow-auto tactical-scroll">
              <div className="grid grid-cols-2 gap-2">
                {topSources.map((s, idx) => (
                  <div key={idx} className="bg-white/5 p-2 rounded border border-white/5 flex justify-between items-center">
                    <span className="text-[9px] text-gray-400 truncate pr-2 uppercase font-tactical">{s.source}</span>
                    <span className="text-[9px] text-osin-emerald font-black">{s.count}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="glass-panel flex-1 flex flex-col min-h-[300px]">
            <div className="p-4 border-b border-white/5 flex justify-between items-center">
              <h2 className="text-xs font-bold font-tactical text-red-500">Live Signal Feed</h2>
              <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
            </div>
            <div className="p-4 flex-1 overflow-auto tactical-scroll">
              <div className="space-y-4">
                {recentEvents.map((event) => (
                  <div key={event.id} className={`p-3 border-l-2 bg-white/5 rounded-r-xl transition-all ${
                    event.severity === 'critical' ? 'border-red-500 bg-red-500/5' : 
                    event.severity === 'high' ? 'border-yellow-500 bg-yellow-500/5' : 'border-osin-emerald bg-white/5'
                  }`}>
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-[9px] font-black uppercase text-white truncate max-w-[120px]">{event.source}</span>
                      <span className={`text-[8px] font-black uppercase px-1 rounded ${
                        event.severity === 'critical' ? 'text-red-500' : 'text-gray-500'
                      }`}>{event.severity}</span>
                    </div>
                    <p className="text-[9px] text-gray-400 line-clamp-2 leading-relaxed mb-2 font-mono">{event.content}</p>
                    <div className="flex justify-between items-center opacity-40">
                       <span className="text-[8px] font-mono">📍 {event.location?.city || 'NODE_U'}</span>
                       <span className="text-[8px] font-mono">✓ {((event.confidence || 0) * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
