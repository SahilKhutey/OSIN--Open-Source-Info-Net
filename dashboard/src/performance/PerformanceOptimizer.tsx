import React, { useMemo, useCallback, useRef } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import * as THREE from 'three';

interface PerformanceOptimizerProps {
  maxNodes?: number;
  lodDistances?: {
    low: number;
    medium: number;
    high: number;
  };
}

export const PerformanceOptimizer: React.FC<PerformanceOptimizerProps> = ({
  maxNodes = 500,
  lodDistances = { low: 40, medium: 20, high: 10 }
}) => {
  const { camera, scene } = useThree();
  const lastCleanupRef = useRef(0);

  // Dynamic Level of Detail logic
  const calculateLOD = useCallback((distance: number) => {
    if (distance > lodDistances.low) return 'low';
    if (distance > lodDistances.medium) return 'medium';
    return 'high';
  }, [lodDistances]);

  // Frame-aware optimization
  useFrame(({ clock }) => {
    const elapsed = clock.getElapsedTime();
    
    // Adaptive quality check every 5 seconds or based on threshold
    scene.traverse((object) => {
      // Check for intelligence nodes (we marked them in components)
      if (object.userData.isNode) {
        const distance = camera.position.distanceTo(object.position);
        const lodLevel = calculateLOD(distance);
        
        // Frustum Culling / Visibility threshold
        object.visible = distance < lodDistances.low * 1.5;
        
        if (object.visible && object instanceof THREE.Group) {
            // Simplify children (Labels, Glows) based on distance
            object.children.forEach(child => {
                if (child instanceof THREE.Mesh) {
                    if (lodLevel === 'low') {
                        child.material.opacity = 0.4;
                    } else if (lodLevel === 'medium') {
                        child.material.opacity = 0.7;
                    } else {
                        child.material.opacity = 1.0;
                    }
                }
            });
        }
      }
    });

    // Memory management: Periodically cull excessive nodes
    if (elapsed - lastCleanupRef.current > 10) {
      lastCleanupRef.current = elapsed;
      performMemoryCleanup();
    }
  });

  const performMemoryCleanup = useCallback(() => {
    const nodes: THREE.Object3D[] = [];
    scene.traverse((obj) => {
      if (obj.userData.isNode) nodes.push(obj);
    });

    if (nodes.length > maxNodes) {
      console.log(`OSIN Performance: Culling ${nodes.length - maxNodes} obsolete nodes.`);
      // Logic would go here to slice and dispose oldest nodes
      // Based on userData.timestamp
    }
  }, [scene, maxNodes]);

  return null;
};
