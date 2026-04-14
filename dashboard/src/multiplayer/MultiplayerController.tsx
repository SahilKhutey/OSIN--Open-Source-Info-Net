import React, { useEffect, useState, useRef, useCallback } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import io, { Socket } from 'socket.io-client';

interface User {
  id: string;
  position: [number, number, number];
  rotation: [number, number, number];
  avatar: string;
  name: string;
}

interface MultiplayerControllerProps {
  onUsersUpdate: (users: User[]) => void;
  onUserJoin: (user: User) => void;
  onUserLeave: (userId: string) => void;
}

const MP_SERVER_URL = 'http://localhost:4000';

export const MultiplayerController: React.FC<MultiplayerControllerProps> = ({
  onUsersUpdate,
  onUserJoin,
  onUserLeave
}) => {
  const [socket, setSocket] = useState<Socket | null>(null);
  const localUserRef = useRef<User | null>(null);

  useEffect(() => {
    const newSocket = io(MP_SERVER_URL, {
      transports: ['websocket'],
      reconnection: true
    });

    newSocket.on('connect', () => {
      console.log('Connected to Collaborative Multiplayer Grid');
      
      const user: User = {
        id: newSocket.id!,
        position: [0, 0, 10],
        rotation: [0, 0, 0],
        avatar: `avatar_${Math.floor(Math.random() * 8)}`,
        name: `Analyst-${newSocket.id?.substring(0, 4).toUpperCase()}`
      };
      
      localUserRef.current = user;
      newSocket.emit('user_join', user);
    });

    newSocket.on('users_update', (usersMap: Record<string, User>) => {
      onUsersUpdate(Object.values(usersMap));
    });

    newSocket.on('user_joined', (user: User) => {
      onUserJoin(user);
    });

    newSocket.on('user_left', (userId: string) => {
      onUserLeave(userId);
    });

    setSocket(newSocket);

    return () => {
      newSocket.disconnect();
    };
  }, [onUsersUpdate, onUserJoin, onUserLeave]);

  // Telemetry stream for movement
  useFrame(({ camera }) => {
    if (socket && localUserRef.current) {
      const pos = camera.position;
      const rot = camera.rotation;

      // Only update if movement delta is significant
      const distance = new THREE.Vector3(pos.x, pos.y, pos.z).distanceTo(
        new THREE.Vector3(...localUserRef.current.position)
      );

      if (distance > 0.05) {
        localUserRef.current.position = [pos.x, pos.y, pos.z];
        localUserRef.current.rotation = [rot.x, rot.y, rot.z];
        socket.emit('update_position', {
          position: localUserRef.current.position,
          rotation: localUserRef.current.rotation
        });
      }
    }
  });

  return null;
};
