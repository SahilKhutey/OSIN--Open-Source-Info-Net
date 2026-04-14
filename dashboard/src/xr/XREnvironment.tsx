import React, { useRef, useEffect, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Line } from '@react-three/drei';
import * as THREE from 'three';
import { HandTracker } from './HandTracker';
import { IntelligenceNode } from './IntelligenceNode';
import { useXRData } from '../hooks/useXRData';
import { GestureController } from './GestureController';

export interface XRNode {
  id: string;
  type: 'threat' | 'opportunity' | 'neutral';
  position: [number, number, number];
  priority: 'critical' | 'high' | 'medium' | 'low';
  data: any;
  connections: string[];
}

export const XREnvironment: React.FC = () => {
  const [nodes, setNodes] = useState<XRNode[]>([]);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const { intelligenceData, connectXR, disconnectXR, sendGesture } = useXRData();

  useEffect(() => {
    connectXR();
    return () => disconnectXR();
  }, [connectXR, disconnectXR]);

  useEffect(() => {
    if (intelligenceData && intelligenceData.length > 0) {
      setNodes(intelligenceData as XRNode[]);
    }
  }, [intelligenceData]);

  const handleNodeSelect = (nodeId: string) => {
    setSelectedNode(nodeId);
    sendGesture(`select_node_${nodeId}`);
  };

  const onGesture = (gesture: string) => {
    console.log('XR Gesture Detected:', gesture);
    if (gesture === 'open_palm') setSelectedNode(null);
  };

  return (
    <div className="w-full h-full relative bg-slate-950 overflow-hidden">
      {/* Hand Tracking Overlay */}
      <HandTracker onGesture={onGesture} />
      
      {/* 3D Environment */}
      <Canvas
        camera={{ position: [0, 0, 10], fov: 75 }}
        onCreated={({ gl }) => {
          gl.setClearColor(new THREE.Color(0x000011));
        }}
      >
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 5]} intensity={1.5} />
        <pointLight position={[-10, -10, -10]} intensity={0.8} />

        {/* Earth Globe */}
        <EarthGlobe />
        
        {/* Intelligence Nodes */}
        {nodes.map((node) => (
          <IntelligenceNode
            key={node.id}
            node={node}
            isSelected={selectedNode === node.id}
            onSelect={handleNodeSelect}
          />
        ))}

        {/* Node Connections */}
        <NodeConnections nodes={nodes} />
        
        {/* Controls */}
        <OrbitControls
          enablePan={true}
          enableZoom={true}
          enableRotate={true}
          minDistance={3}
          maxDistance={25}
        />

        {/* Gesture Controller */}
        <GestureController onNodeSelect={handleNodeSelect} nodes={nodes} />
      </Canvas>

      {/* UI Overlay */}
      <div className="absolute top-6 left-6 text-white font-mono pointer-events-none z-10">
        <h2 className="text-2xl font-bold text-cyan-400 tracking-tighter uppercase mb-2">OSIN XR COMMAND</h2>
        <div className="space-y-1 text-sm bg-black/40 backdrop-blur-md p-4 rounded-lg border border-cyan-500/30">
          <p className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-cyan-500 animate-pulse"></span> Nodes Tracked: {nodes.length}</p>
          <p className="flex items-center gap-2 underline decoration-cyan-500/50">Selected Identification: <span className="text-cyan-400">{selectedNode || 'NONE'}</span></p>
          <div className="mt-4 pt-4 border-t border-white/10 space-y-1 opacity-70">
            <p>🤏 PINCH: SELECT NODE</p>
            <p>✋ OPEN PALM: RESET SELECTION</p>
            <p>👆 POINT: TARGET HIGHLIGHT</p>
          </div>
        </div>
      </div>
    </div>
  );
};

const EarthGlobe: React.FC = () => {
  const earthRef = useRef<THREE.Mesh>(null);

  useFrame(({ clock }) => {
    if (earthRef.current) {
      earthRef.current.rotation.y = clock.getElapsedTime() * 0.05;
    }
  });

  return (
    <mesh ref={earthRef}>
      <sphereGeometry args={[3, 64, 64]} />
      <meshStandardMaterial
        color={0x112244}
        emissive={0x004488}
        emissiveIntensity={0.2}
        roughness={0.7}
        metalness={0.3}
        wireframe
      />
      
      {/* Interior glow */}
      <mesh scale={[0.98, 0.98, 0.98]}>
        <sphereGeometry args={[3, 32, 32]} />
        <meshBasicMaterial
          color={0x001122}
          transparent
          opacity={0.8}
        />
      </mesh>
      
      {/* Atmospheric glow */}
      <mesh scale={[1.15, 1.15, 1.15]}>
        <sphereGeometry args={[3, 32, 32]} />
        <meshBasicMaterial
          color={0x0088ff}
          transparent
          opacity={0.05}
          side={THREE.BackSide}
        />
      </mesh>
    </mesh>
  );
};

const NodeConnections: React.FC<{ nodes: XRNode[] }> = ({ nodes }) => {
  const connections: THREE.Vector3[][] = [];

  nodes.forEach((node) => {
    if (node.connections) {
      node.connections.forEach((connectionId) => {
        const targetNode = nodes.find(n => n.id === connectionId);
        if (targetNode) {
          connections.push([
            new THREE.Vector3(...node.position),
            new THREE.Vector3(...targetNode.position)
          ]);
        }
      });
    }
  });

  return (
    <>
      {connections.map((points, index) => (
        <Line
          key={index}
          points={points}
          color="#06b6d4"
          lineWidth={1}
          transparent
          opacity={0.4}
        />
      ))}
    </>
  );
};
