import React from 'react';

const HexGridLoading: React.FC = () => {
    return (
        <div className="absolute inset-0 z-[999] bg-black flex flex-col items-center justify-center gap-8 font-mono">
            <div className="relative w-24 h-24">
                {/* Visual Hexagonal Grid Animation (CSS-only) */}
                <div className="absolute inset-0 border-2 border-osin-emerald opacity-20 rotate-45 animate-pulse" />
                <div className="absolute inset-2 border border-osin-cyan opacity-40 -rotate-45 animate-ping" />
                <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-4 h-4 bg-osin-emerald shadow-[0_0_15px_#10b981] rotate-45 animate-spin" />
                </div>
                
                {/* Hex Corners (Representational) */}
                {[0, 60, 120, 180, 240, 300].map(deg => (
                    <div 
                        key={deg} 
                        className="absolute top-1/2 left-1/2 w-1 h-1 bg-osin-emerald"
                        style={{ transform: `rotate(${deg}deg) translateY(-48px)` }}
                    />
                ))}
            </div>

            <div className="flex flex-col items-center gap-2">
                <div className="text-osin-emerald text-sm font-black tracking-[0.4em] uppercase">
                    Syncing Intelligence Grid
                </div>
                <div className="flex gap-1">
                    {[1, 2, 3].map(i => (
                        <div 
                            key={i} 
                            className="w-1.5 h-1.5 bg-osin-cyan animate-bounce" 
                            style={{ animationDelay: `${i * 0.2}s` }} 
                        />
                    ))}
                </div>
            </div>

            <style>{`
                @keyframes pulse-custom {
                    0%, 100% { transform: scale(1); opacity: 0.2; }
                    50% { transform: scale(1.1); opacity: 0.5; }
                }
                .hex-animate {
                    animation: pulse-custom 2s infinite ease-in-out;
                }
            `}</style>
        </div>
    );
};

export default HexGridLoading;
