import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { GlobeProps } from '../../types/command_center';

const GlobeVisualization: React.FC<GlobeProps> = ({ 
  alerts, 
  onAlertSelect, 
  onGlobeClick, 
  className 
}) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene>();
  const rendererRef = useRef<THREE.WebGLRenderer>();
  const cameraRef = useRef<THREE.PerspectiveCamera>();
  const globeRef = useRef<THREE.Mesh>();

  useEffect(() => {
    if (!mountRef.current) return;

    // Initialize Three.js
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, mountRef.current.clientWidth / mountRef.current.clientHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    
    renderer.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight);
    mountRef.current.appendChild(renderer.domElement);

    // Create globe - using a high-fidelity planetary texture
    const geometry = new THREE.SphereGeometry(5, 64, 64);
    const textureLoader = new THREE.TextureLoader();
    const texture = textureLoader.load('https://unpkg.com/three-globe/example/img/earth-night.jpg');
    const bumpMap = textureLoader.load('https://unpkg.com/three-globe/example/img/earth-topology.png');
    
    const material = new THREE.MeshPhongMaterial({ 
      map: texture,
      bumpMap: bumpMap,
      bumpScale: 0.05,
      specular: new THREE.Color('#010101')
    });
    
    const globe = new THREE.Mesh(geometry, material);
    scene.add(globe);

    // Add lighting
    const ambientLight = new THREE.AmbientLight(0x404040, 2);
    scene.add(ambientLight);
    const directionalLight = new THREE.DirectionalLight(0x00ffff, 1);
    directionalLight.position.set(5, 3, 5);
    scene.add(directionalLight);

    // Position camera
    camera.position.z = 15;

    // Add alert markers as glowing spikes
    const markers: THREE.Group = new THREE.Group();
    alerts.forEach(alert => {
      if (alert.location) {
        const markerGeometry = new THREE.CylinderGeometry(0.05, 0, 1.5, 8);
        const markerMaterial = new THREE.MeshBasicMaterial({ 
          color: getAlertColor(alert.level),
          transparent: true,
          opacity: 0.8
        });
        const marker = new THREE.Mesh(markerGeometry, markerMaterial);
        
        // Convert lat/lon to 3D position
        const phi = (90 - alert.location.lat) * Math.PI / 180;
        const theta = (alert.location.lon + 180) * Math.PI / 180;
        
        // Move to surface and offset by half height so base is on globe
        const r = 5;
        marker.position.set(
          r * Math.sin(phi) * Math.cos(theta),
          r * Math.cos(phi),
          r * Math.sin(phi) * Math.sin(theta)
        );
        
        // Orient towards center (upwards from surface)
        marker.quaternion.setFromUnitVectors(
          new THREE.Vector3(0, 1, 0),
          marker.position.clone().normalize()
        );
        
        markers.add(marker);
      }
    });
    scene.add(markers);

    // Animation loop
    const animate = () => {
      const frameId = requestAnimationFrame(animate);
      globe.rotation.y += 0.002;
      markers.rotation.y += 0.002; // Keep markers synced with globe
      renderer.render(scene, camera);
    };
    animate();

    // Resize handling
    const handleResize = () => {
      if (!mountRef.current) return;
      camera.aspect = mountRef.current.clientWidth / mountRef.current.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight);
    };
    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      if (mountRef.current) {
        mountRef.current.removeChild(renderer.domElement);
      }
      renderer.dispose();
      geometry.dispose();
      material.dispose();
    };
  }, [alerts]);

  const getAlertColor = (level: string): number => {
    switch (level) {
      case 'CRITICAL': return 0xff0000;
      case 'HIGH': return 0xff5500;
      case 'MEDIUM': return 0xffff00;
      case 'LOW': return 0x00ff00;
      default: return 0xffffff;
    }
  };

  return <div ref={mountRef} className={className} style={{ width: '100%', height: '100%', minHeight: '400px' }} />;
};

export default GlobeVisualization;
