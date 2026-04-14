import React, { useRef, useMemo, useState, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import { Stars, Float } from '@react-three/drei';
import * as THREE from 'three';
import { Bloom, EffectComposer, Vignette } from '@react-three/postprocessing';

const EARTH_DAY = 'https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg';
const EARTH_NIGHT = 'https://unpkg.com/three-globe/example/img/earth-night-lights.jpg';
const EARTH_CLOUDS = 'https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/earth_clouds_2048.png';

const TranscendentEarth: React.FC = () => {
  const earthRef = useRef<THREE.Mesh>(null!);
  const cloudsRef = useRef<THREE.Mesh>(null!);
  const atmosphereRef = useRef<THREE.Mesh>(null!);

  const [textures, setTextures] = useState<{
    day: THREE.Texture | null;
    night: THREE.Texture | null;
    clouds: THREE.Texture | null;
  }>({ day: null, night: null, clouds: null });

  const [isReady, setIsReady] = useState(false);
  const [error, setError] = useState(false);

  useEffect(() => {
    const loader = new THREE.TextureLoader();
    const loadTexture = (url: string) => {
      return new Promise<THREE.Texture>((resolve, reject) => {
        loader.load(url, resolve, undefined, reject);
      });
    };

    Promise.allSettled([
      loadTexture(EARTH_DAY),
      loadTexture(EARTH_NIGHT),
      loadTexture(EARTH_CLOUDS)
    ]).then((results) => {
      const successData = results.map(r => r.status === 'fulfilled' ? r.value : null);
      setTextures({
        day: successData[0],
        night: successData[1],
        clouds: successData[2]
      });
      if (results.some(r => r.status === 'rejected')) {
        console.warn("OSIN Visuals: Some Earth textures failed to load. Using procedural fallbacks.");
        setError(true);
      }
      
      // Delay mounting of post-processing to ensure GPU context is steady
      setTimeout(() => setIsReady(true), 1500);
    });
  }, []);

  const earthMaterial = useMemo(() => {
    if (!textures.day && !textures.night) {
      // High-quality procedural fallback
      return new THREE.MeshPhongMaterial({
        color: new THREE.Color(0x0a1a2f),
        emissive: new THREE.Color(0x002244),
        specular: new THREE.Color(0x111111),
        shininess: 25,
      });
    }

    return new THREE.MeshPhongMaterial({
      map: textures.day || undefined,
      emissiveMap: textures.night || undefined,
      emissive: new THREE.Color(0xffff88),
      emissiveIntensity: textures.night ? 0.5 : 0,
      specular: new THREE.Color(0x333333),
      shininess: 15,
      color: textures.day ? 0xffffff : 0x0a1a2f
    });
  }, [textures.day, textures.night]);

  const cloudMaterial = useMemo(() => {
    return new THREE.MeshPhongMaterial({
      map: textures.clouds || undefined,
      color: textures.clouds ? 0xffffff : 0x444444,
      transparent: true,
      opacity: textures.clouds ? 0.4 : 0.1,
      blending: THREE.AdditiveBlending,
      side: THREE.DoubleSide,
    });
  }, [textures.clouds]);

  useFrame(({ clock }) => {
    if (!earthRef.current || !cloudsRef.current || !atmosphereRef.current) return;
    
    const time = clock.getElapsedTime();
    
    // Rotate Earth
    earthRef.current.rotation.y = time * 0.05;
    
    // Rotate Clouds slightly faster for parallax
    cloudsRef.current.rotation.y = time * 0.07;
    cloudsRef.current.rotation.x = Math.sin(time * 0.01) * 0.02;
    
    // Pulse atmosphere
    atmosphereRef.current.scale.setScalar(5.15 + Math.sin(time * 1.5) * 0.02);
  });

  return (
    <>
      <Stars radius={300} depth={60} count={20000} factor={7} saturation={0} fade speed={1} />
      
      <Float speed={1.5} rotationIntensity={0.5} floatIntensity={0.5}>
        {/* Core Earth */}
        <mesh ref={earthRef}>
          <sphereGeometry args={[5, 128, 128]} />
          <primitive object={earthMaterial} attach="material" />
        </mesh>

        {/* Clouds Layer */}
        <mesh ref={cloudsRef}>
          <sphereGeometry args={[5.05, 128, 128]} />
          <primitive object={cloudMaterial} attach="material" />
        </mesh>

        {/* Atmospheric Glow */}
        <mesh ref={atmosphereRef}>
          <sphereGeometry args={[5.15, 128, 128]} />
          <meshBasicMaterial
            color={0x0077ff}
            transparent
            opacity={0.1}
            blending={THREE.AdditiveBlending}
            side={THREE.BackSide}
          />
        </mesh>
      </Float>

      {/* Strategic Lighting */}
      <ambientLight intensity={0.2} />
      <directionalLight position={[10, 5, 7]} intensity={2.5} />
      <pointLight position={[-10, -5, -10]} color={0x0077ff} intensity={2} />
      
      {/* Visual Excellence Filters - Recreated on texture state change for stability */}
      <EffectComposer key={textures.day ? 'with-textures' : 'no-textures'} disableNormalPass>
        <Bloom 
          luminanceThreshold={0.5} 
          intensity={1.2} 
          radius={0.4} 
        />
        <Vignette eskil={false} offset={0.1} darkness={1.1} />
      </EffectComposer>

      {/* Error Indicator (Subtle) */}
      {error && (
        <group position={[0, -7, 0]}>
           {/* Non-intrusive metadata about visual degradation */}
        </group>
      )}
    </>
  );
};

export default TranscendentEarth;
