import { useState, useEffect, useCallback, useRef } from 'react';
import { io, Socket } from 'socket.io-client';

interface XRDataHook {
  intelligenceData: any[];
  connectXR: () => void;
  disconnectXR: () => void;
  sendGesture: (gesture: string) => void;
}

const SOCKET_URL = 'http://localhost:3001';

export const useXRData = (): XRDataHook => {
  const [intelligenceData, setIntelligenceData] = useState<any[]>([]);
  const socketRef = useRef<Socket | null>(null);

  const connectXR = useCallback(() => {
    if (socketRef.current?.connected) return;

    socketRef.current = io(SOCKET_URL, {
      transports: ['websocket'],
      reconnection: true,
      reconnectionAttempts: 5
    });

    socketRef.current.on('connect', () => {
      console.log('Connected to OSIN XR Intelligence Bridge');
    });

    socketRef.current.on('intelligence_update', (data: any) => {
      setIntelligenceData(prev => {
        // Prevent duplicates and update existing nodes
        const index = prev.findIndex(item => item.id === data.id);
        if (index !== -1) {
            const updated = [...prev];
            updated[index] = data;
            return updated;
        }
        return [...prev, data];
      });
    });

    socketRef.current.on('intelligence_batch', (data: any[]) => {
      setIntelligenceData(data);
    });

    socketRef.current.on('gesture_feedback', (data: any) => {
        // Handle server-side gesture processing feedback
        window.dispatchEvent(new CustomEvent('osin_gesture_event', { detail: data }));
    });

    socketRef.current.on('disconnect', () => {
      console.log('Disconnected from XR Bridge');
    });
  }, []);

  const disconnectXR = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.disconnect();
    }
  }, []);

  const sendGesture = useCallback((gesture: string) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit('xr_gesture', {
        gesture,
        timestamp: Date.now()
      });
    }

    // Also dispatch locally for immediate feedback in the UI components
    window.dispatchEvent(new CustomEvent('osin_gesture_event', { detail: { gesture } }));
  }, []);

  useEffect(() => {
    return () => {
      disconnectXR();
    };
  }, [disconnectXR]);

  return {
    intelligenceData,
    connectXR,
    disconnectXR,
    sendGesture
  };
};
