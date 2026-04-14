import React, { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { useTexture, Stars, Float } from '@react-three/drei';
import * as THREE from 'three';
import { Bloom, EffectComposer, Vignette } from '@react-three/postprocessing';

const EARTH_DAY = 'https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg';
const EARTH_NIGHT = 'https://unpkg.com/three-globe/example/img/earth-night-lights.jpg';
const EARTH_CLOUDS = 'https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/earth_clouds_2048.png';

const TranscendentEarth: React.FC = () => {
  const earthRef = useRef<THREE.Mesh>(null!);
  const cloudsRef = useRef<THREE.Mesh>(null!);
  const atmosphereRef = useRef<THREE.Mesh>(null!);

  const [dayTexture, nightTexture, cloudTexture] = useTexture([EARTH_DAY, EARTH_NIGHT, EARTH_CLOUDS]);

  const earthMaterial = useMemo(() => {
    return new THREE.MeshPhongMaterial({
      map: dayTexture,
      emissiveMap: nightTexture,
      emissive: new THREE.Color(0xffff88),
      emissiveIntensity: 0.5,
      specular: new THREE.Color(0x333333),
      shininess: 15,
    });
  }, [dayTexture, nightTexture]);

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
          <meshPhongMaterial
            map={cloudTexture}
            transparent
            opacity={0.4}
            blending={THREE.AdditiveBlending}
            side={THREE.DoubleSide}
          />
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
      
      {/* Visual Excellence Filters */}
      <EffectComposer>
        <Bloom 
          luminanceThreshold={0.5} 
          mipmapBlur 
          intensity={1.5} 
          radius={0.4} 
        />
        <Vignette eskil={false} offset={0.1} darkness={1.1} />
      </EffectComposer>
    </>
  );
};

export default TranscendentEarth;
