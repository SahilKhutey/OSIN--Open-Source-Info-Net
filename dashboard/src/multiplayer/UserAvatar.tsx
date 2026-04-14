import React from 'react';
import { Sphere, Text } from '@react-three/drei';
import * as THREE from 'three';

interface User {
  id: string;
  position: [number, number, number];
  rotation: [number, number, number];
  avatar: string;
  name: string;
}

export const UserAvatar: React.FC<{ user: User }> = ({ user }) => {
  return (
    <group position={new THREE.Vector3(...user.position)}>
      {/* Visual Avatar - Holographic Prism */}
      <mesh rotation={new THREE.Euler(...user.rotation)}>
        <octahedronGeometry args={[0.2, 0]} />
        <meshStandardMaterial 
            color="#06b6d4" 
            transparent 
            opacity={0.6} 
            emissive="#06b6d4"
            emissiveIntensity={1}
            wireframe
        />
      </mesh>
      
      {/* Interior Identity Core */}
      <Sphere args={[0.08, 8, 8]}>
        <meshBasicMaterial color="#ffffff" />
      </Sphere>
      
      {/* Tactical Label */}
      <Text
        position={[0, 0.6, 0]}
        fontSize={0.12}
        color="cyan"
        font="/fonts/JetBrainsMono-Bold.ttf"
        anchorX="center"
        anchorY="bottom"
      >
        {user.name.toUpperCase()}
      </Text>
      
      {/* Dynamic Status Indicator */}
      <mesh position={[0, 0.45, 0]}>
        <sphereGeometry args={[0.03, 8, 8]} />
        <meshBasicMaterial color="#00ff00" />
      </mesh>
    </group>
  );
};
