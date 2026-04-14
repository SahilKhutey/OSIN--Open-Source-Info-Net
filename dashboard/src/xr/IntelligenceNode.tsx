import React, { useRef, useState } from 'react';
import { Sphere, Text, Html } from '@react-three/drei';
import * as THREE from 'three';
import { XRNode } from './XREnvironment';

interface IntelligenceNodeProps {
  node: XRNode;
  isSelected: boolean;
  onSelect: (nodeId: string) => void;
}

export const IntelligenceNode: React.FC<IntelligenceNodeProps> = ({
  node,
  isSelected,
  onSelect
}) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);

  const getNodeColor = () => {
    switch (node.priority) {
      case 'critical': return '#ff4444';
      case 'high': return '#facc15';
      case 'medium': return '#22d3ee';
      case 'low': return '#4ade80';
      default: return '#94a3b8';
    }
  };

  const getNodeSize = () => {
    switch (node.priority) {
      case 'critical': return 0.4;
      case 'high': return 0.35;
      case 'medium': return 0.3;
      case 'low': return 0.25;
      default: return 0.2;
    }
  };

  const handleClick = (e: any) => {
    e.stopPropagation();
    onSelect(node.id);
  };

  return (
    <group position={new THREE.Vector3(...node.position)}>
      {/* Interaction Surface */}
      <Sphere
        ref={meshRef}
        args={[getNodeSize(), 16, 16]}
        onClick={handleClick}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <meshStandardMaterial
          color={getNodeColor()}
          emissive={isSelected ? getNodeColor() : '#000000'}
          emissiveIntensity={isSelected ? 1.5 : 0}
          transparent
          opacity={hovered || isSelected ? 1 : 0.6}
          roughness={0.2}
          metalness={0.8}
        />
      </Sphere>

      {/* Pulse effect for critical nodes */}
      {node.priority === 'critical' && (
        <Sphere args={[getNodeSize() * 2, 16, 16]}>
            <meshBasicMaterial
                color={getNodeColor()}
                transparent
                opacity={0.1}
                side={THREE.BackSide}
            />
        </Sphere>
      )}

      {/* Selection Glow */}
      {isSelected && (
        <Sphere args={[getNodeSize() * 1.6, 16, 16]}>
          <meshBasicMaterial
            color={getNodeColor()}
            transparent
            opacity={0.15}
            side={THREE.BackSide}
          />
        </Sphere>
      )}

      {/* Type Label */}
      {(hovered || isSelected) && (
        <Text
          position={[0, getNodeSize() + 0.3, 0]}
          fontSize={0.18}
          color="white"
          font="/fonts/JetBrainsMono-Bold.ttf"
          anchorX="center"
          anchorY="bottom"
        >
          {node.type.toUpperCase()}
        </Text>
      )}

      {/* Detailed Info Panel */}
      {isSelected && (
        <Html
          position={[0, getNodeSize() + 0.6, 0]}
          distanceFactor={12}
          className="pointer-events-auto"
        >
          <div className="w-64 bg-slate-950/90 border-2 border-cyan-500/50 p-4 rounded-xl shadow-2xl backdrop-blur-xl font-mono text-white select-none">
            <div className="flex justify-between items-start mb-3">
              <div>
                <h3 className="text-cyan-400 font-bold text-xs">IDENT_ID: {node.id.substring(0, 8)}</h3>
                <p className="text-[10px] text-slate-500 uppercase tracking-widest">{node.priority} PRIORITY</p>
              </div>
              <div className={`w-3 h-3 rounded-full animate-ping ${
                node.priority === 'critical' ? 'bg-red-500' : 'bg-cyan-500'
              }`}></div>
            </div>
            
            <div className="space-y-2 text-[11px] border-y border-white/5 py-3 mb-3">
              <p><span className="text-slate-500">CATEGORY:</span> {node.type}</p>
              <p><span className="text-slate-500">COORD:</span> {node.position.map(p => p.toFixed(2)).join(', ')}</p>
              <p><span className="text-slate-500">CONFIDENCE:</span> {(Math.random() * 20 + 80).toFixed(1)}%</p>
            </div>

            <button
              onClick={() => console.log('Deep analysis:', node)}
              className="w-full bg-cyan-600 hover:bg-cyan-500 text-white text-[10px] py-2 rounded font-bold uppercase tracking-widest transition-colors"
            >
              Initialize Deep Link
            </button>
          </div>
        </Html>
      )}
    </group>
  );
};
