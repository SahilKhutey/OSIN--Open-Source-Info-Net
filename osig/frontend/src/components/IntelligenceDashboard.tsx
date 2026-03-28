import React, { useState, useEffect } from 'react';

const IntelligenceDashboard: React.FC = () => {
    const [status, setStatus] = useState("INITIALIZING");
    
    useEffect(() => {
        console.log("OSIG: Tactical Dashboard mounting...");
        setStatus("OPERATIONAL");
    }, []);

    return (
        <div className="osig-dashboard bg-slate-900 text-green-400 p-6 min-h-screen font-mono">
            <header className="flex justify-between items-center border-b border-green-900 pb-4 mb-6">
                <h1 className="text-2xl font-bold tracking-tighter">
                    OSIG <span className="text-green-600">INTEL GRID</span>
                </h1>
                <div className="flex gap-4">
                    <span className="animate-pulse text-xs bg-green-900/30 px-2 py-1 border border-green-800">
                        STATUS: {status}
                    </span>
                    <button className="bg-red-900/20 border border-red-800 text-red-500 px-3 py-1 text-xs hover:bg-red-900/40 transition-colors">
                        EMERGENCY PROTOCOL
                    </button>
                </div>
            </header>

            <main className="grid grid-cols-12 gap-6">
                {/* Left: Global Heatmap & Alerts */}
                <section className="col-span-4 space-y-6">
                    <div className="bg-slate-800/50 border border-slate-700 h-96 flex items-center justify-center">
                        <span className="text-slate-500">[GLOBAL HEATMAP SUBSTRATE]</span>
                    </div>
                    <div className="bg-slate-800/20 border border-slate-700 p-4 min-h-[200px]">
                        <h2 className="text-xs uppercase text-slate-400 mb-2">Realtime Alert Console</h2>
                        <div className="space-y-1 text-[10px]">
                            <p className="text-yellow-600 font-bold">[ALPHA-01] COORDINATED SIGNAL CLUSTER DETECTED - EU NORTH</p>
                            <p className="text-red-600 font-bold">[CRITICAL] FINANCIAL ANOMALY: FLASH CRASH ATOMIC INITIATED</p>
                        </div>
                    </div>
                </section>

                {/* Center: Intelligence Stream & Analysis */}
                <section className="col-span-5 space-y-6">
                    <div className="bg-slate-800/50 border border-slate-700 p-4 h-[600px] overflow-hidden relative">
                        <h2 className="text-xs uppercase text-slate-400 mb-4 font-bold border-b border-slate-700 pb-2">
                            Tactical Event Stream
                        </h2>
                        <div className="space-y-4 opacity-70">
                            {[1,2,3,4,5].map(i => (
                                <div key={i} className="border-l-2 border-green-800 pl-4 py-1">
                                    <div className="text-[10px] text-green-600 mb-1">T+ {new Date().toLocaleTimeString()} | CONFIDENCE: 0.92</div>
                                    <div className="text-sm">Semantic signal fusion complete for regional proxy {i}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                </section>

                {/* Right: Predictive & HUD */}
                <section className="col-span-3 space-y-6">
                    <div className="bg-slate-800/80 border border-slate-700 p-4 h-64">
                        <h2 className="text-xs uppercase text-slate-400 mb-2">Threat Matrix</h2>
                        <div className="flex items-center justify-center p-8">
                             <div className="w-32 h-32 border-2 border-slate-700 rounded-full flex items-center justify-center">
                                <div className="text-center">
                                    <div className="text-xl font-bold">42%</div>
                                    <div className="text-[8px]">RISK LEVEL</div>
                                </div>
                             </div>
                        </div>
                    </div>
                    <div className="bg-slate-800/80 border border-slate-700 p-4 h-64">
                         <h2 className="text-xs uppercase text-slate-400 mb-2">Explainable AI Reasoning</h2>
                         <p className="text-[10px] text-slate-500 leading-relaxed">
                            Awaiting event selection for forensic reasoning breakdown...
                         </p>
                    </div>
                </section>
            </main>

            <footer className="mt-6 border-t border-slate-800 pt-4 flex justify-between text-[10px] text-slate-500 italic">
                <span>SYSTEM UPTIME: 142.1h</span>
                <span>OSIG KNOWLEDGE GRAPH: 12.4M NODES</span>
            </footer>
        </div>
    );
};

export default IntelligenceDashboard;
