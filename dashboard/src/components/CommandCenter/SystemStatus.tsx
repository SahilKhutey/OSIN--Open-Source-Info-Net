import React from 'react';
import { SystemStatus as SystemStatusType } from '../../types/command_center';
import { Activity, Shield, Cpu, Zap, Globe } from 'lucide-react';

interface SystemStatusProps {
  status: SystemStatusType;
}

const SystemStatus: React.FC<SystemStatusProps> = ({ status }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACTIVE':
      case 'ONLINE':
      case 'STABLE':
        return 'text-cyan-400';
      case 'DEGRADED':
      case 'SYNCING':
      case 'LOADING':
        return 'text-amber-400';
      case 'OFFLINE':
      case 'CRITICAL':
        return 'text-rose-500';
      default:
        return 'text-gray-500';
    }
  };

  const StatusRow = ({ label, val, icon: Icon }: any) => (
    <div className="flex justify-between items-center py-2 border-b border-white/5">
      <div className="flex items-center gap-2">
        <Icon size={14} className="opacity-40" />
        <span className="text-[10px] uppercase tracking-wider opacity-60 font-medium">{label}</span>
      </div>
      <span className={`text-[10px] font-bold tracking-widest ${getStatusColor(val)}`}>
        {val}
      </span>
    </div>
  );

  return (
    <div className="h-full flex flex-col">
      <h2 className="text-cyan-500 text-sm font-bold tracking-widest mb-6 flex items-center gap-2">
        <Activity size={16} />
        NODE INFRASTRUCTURE
      </h2>
      
      <div className="space-y-2 flex-1">
        <StatusRow label="Ingestion Layer" val={status.ingestion} icon={Zap} />
        <StatusRow label="OSIN Graph Core" val={status.graphCore} icon={Globe} />
        <StatusRow label="Autonomous Logic" val={status.aiReasoning} icon={Cpu} />
        <StatusRow label="Threat Posture" val={status.threatLevel} icon={Shield} />
        
        <div className="mt-10 pt-4 bg-cyan-950/10 rounded-lg p-4 border border-cyan-500/10">
          <div className="flex justify-between items-center mb-4">
            <span className="text-[10px] font-bold tracking-widest opacity-80 uppercase">World Risk index</span>
            <span className="text-xs font-mono text-cyan-400">{status.globalRisk}%</span>
          </div>
          <div className="w-full bg-black/50 rounded-full h-1.5 overflow-hidden">
            <div 
              className="bg-gradient-to-right from-cyan-500 to-blue-500 h-full transition-all duration-1000 ease-out"
              style={{ width: `${status.globalRisk}%`, backgroundColor: '#00f2ff', boxShadow: '0 0 10px rgba(0, 242, 255, 0.5)' }}
            ></div>
          </div>
          <p className="text-[8px] mt-4 opacity-40 leading-relaxed uppercase tracking-tighter">
            Global stability audit complete. No critical systemic cascading failures projected in the next 120s cycle.
          </p>
        </div>
      </div>
    </div>
  );
};

export default SystemStatus;
