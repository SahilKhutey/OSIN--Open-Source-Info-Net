import React, { useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface TerrainLayerProps {
  elevationData?: {
    center: number;
    max: number;
    min: number;
  };
  opacity: number;
}

export const TerrainLayer: React.FC<TerrainLayerProps> = ({ elevationData, opacity }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  
  // Calculate a visual displacement factor based on terrain profile
  // In a real app, this would drive a vertex shader with a displacement map.
  const displacementScale = useMemo(() => {
    if (!elevationData) return 1.0;
    const range = elevationData.max - elevationData.min;
    return 1.0 + (range / 10000); // 1000m diff = 10% bump
  }, [elevationData]);

  useFrame((state) => {
    if (meshRef.current) {
      // Subtle pulse to indicate 'active' analysis
      const pulse = Math.sin(state.clock.elapsedTime * 2) * 0.002;
      meshRef.current.scale.set(
        displacementScale + pulse,
        displacementScale + pulse,
        displacementScale + pulse
      );
    }
  });

  if (!elevationData) return null;

  return (
    <mesh ref={meshRef}>
      <sphereGeometry args={[1.01, 128, 128]} />
      <meshStandardMaterial 
        color="#8B4513"
        transparent
        opacity={opacity * 0.5}
        wireframe={true}
        emissive="#DAA520"
        emissiveIntensity={0.2}
      />
    </mesh>
  );
};

export default TerrainLayer;
