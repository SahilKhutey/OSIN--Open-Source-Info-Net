import React, { useEffect, useRef } from 'react';
import { useThree, useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface GestureControllerProps {
  onNodeSelect: (nodeId: string) => void;
  nodes: any[];
}

export const GestureController: React.FC<GestureControllerProps> = ({
  onNodeSelect,
  nodes
}) => {
  const { camera, scene, raycaster, mouse } = useThree();
  const lastGestureRef = useRef<string | null>(null);

  useEffect(() => {
    const handleGesture = (event: CustomEvent) => {
      const gesture = event.detail.gesture;
      
      if (gesture !== lastGestureRef.current) {
        lastGestureRef.current = gesture;
        
        switch (gesture) {
          case 'pinch':
            selectTargetedNode();
            break;
          case 'point':
            // Highlighting is handled by R3F pointer events in the node component,
            // but we could trigger global UI states here.
            break;
          case 'open_palm':
            // Reset logic
            break;
        }
      }
    };

    window.addEventListener('osin_gesture_event', handleGesture as EventListener);
    
    return () => {
      window.removeEventListener('osin_gesture_event', handleGesture as EventListener);
    };
  }, [nodes, camera, scene, raycaster]);

  const selectTargetedNode = () => {
    // Raycast from current targeting position
    // If targeted by 'point' gesture, mouse coordinates would be mapped from hand position.
    // For now, we use screen center (targeting reticle logic).
    
    raycaster.setFromCamera(new THREE.Vector2(0, 0), camera);
    const intersects = raycaster.intersectObjects(scene.children, true);
    
    // Filter for intelligence nodes (Spheres)
    const nodeIntersects = intersects.filter(i => 
      i.object.type === 'Mesh' && 
      (i.object as THREE.Mesh).geometry.type === 'SphereGeometry'
    );

    if (nodeIntersects.length > 0) {
      // Find the ID from parent group if necessary, or check custom data
      // In this impl, components handle their own clicks, but this is the gesture fallback
      console.log('Gesture Selection Intersected:', nodeIntersects[0].object);
    }
  };

  return null;
};
