import React, { useEffect, useRef } from 'react';
import { Hands, HAND_CONNECTIONS } from '@mediapipe/hands';
import { Camera } from '@mediapipe/camera_utils';

interface HandTrackerProps {
  onGesture: (gesture: string) => void;
}

export const HandTracker: React.FC<HandTrackerProps> = ({ onGesture }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const hands = new Hands({
      locateFile: (file) => {
        return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
      }
    });

    hands.setOptions({
      maxNumHands: 2,
      modelComplexity: 1,
      minDetectionConfidence: 0.7,
      minTrackingConfidence: 0.7
    });

    hands.onResults((results) => {
      if (canvasRef.current && videoRef.current) {
        const ctx = canvasRef.current.getContext('2d');
        if (ctx) {
          ctx.save();
          ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
          
          if (results.multiHandLandmarks) {
            for (const landmarks of results.multiHandLandmarks) {
              drawConnectors(ctx, landmarks, HAND_CONNECTIONS, {
                color: '#06b6d4',
                lineWidth: 2
              });
              drawLandmarks(ctx, landmarks, {
                color: '#ff4444',
                lineWidth: 1
              });
            }

            // Gesture detection
            detectGestures(results.multiHandLandmarks, onGesture);
          }
          
          ctx.restore();
        }
      }
    });

    const camera = new Camera(videoRef.current!, {
      onFrame: async () => {
        await hands.send({ image: videoRef.current! });
      },
      width: 640,
      height: 480
    });

    camera.start();

    return () => {
      camera.stop();
    };
  }, [onGesture]);

  const detectGestures = (landmarks: any[], callback: (gesture: string) => void) => {
    if (landmarks.length > 0) {
      const hand = landmarks[0];
      
      // Pinch detection (thumb and index finger)
      const thumbTip = hand[4];
      const indexTip = hand[8];
      const distance = Math.hypot(
        thumbTip.x - indexTip.x,
        thumbTip.y - indexTip.y,
        thumbTip.z - indexTip.z
      );

      if (distance < 0.04) {
        callback('pinch');
      }

      // Open palm detection
      const fingersExtended = checkFingersExtended(hand);
      if (fingersExtended === 5) {
        callback('open_palm');
      }

      // Point detection
      if (fingersExtended === 1 && isIndexExtended(hand)) {
        callback('point');
      }
    }
  };

  const checkFingersExtended = (landmarks: any[]): number => {
    let extendedCount = 0;
    const fingerTips = [4, 8, 12, 16, 20];
    
    fingerTips.forEach((tipIndex, fingerIndex) => {
      if (isFingerExtended(landmarks, tipIndex, fingerIndex)) {
        extendedCount++;
      }
    });

    return extendedCount;
  };

  const isFingerExtended = (landmarks: any[], tipIndex: number, fingerIndex: number): boolean => {
    // Thumb is special (horizontal check)
    if (fingerIndex === 0) {
        return landmarks[tipIndex].x < landmarks[tipIndex - 1].x;
    }
    return landmarks[tipIndex].y < landmarks[tipIndex - 2].y;
  };

  const isIndexExtended = (landmarks: any[]): boolean => {
    return landmarks[8].y < landmarks[6].y && landmarks[6].y < landmarks[5].y;
  };

  return (
    <div className="absolute top-6 right-6 w-80 h-60 border-2 border-cyan-500/50 rounded-xl bg-slate-900/40 backdrop-blur-sm overflow-hidden z-20 shadow-2xl shadow-cyan-500/10">
      <video
        ref={videoRef}
        className="hidden"
        width="640"
        height="480"
      />
      <canvas
        ref={canvasRef}
        width="640"
        height="480"
        className="w-full h-full object-cover scale-x-[-1] opacity-60"
      />
      <div className="absolute bottom-2 left-3 text-[10px] text-cyan-400 font-mono tracking-widest opacity-80">
        AI PERCEPTION ACTIVE // HND_TRK_01
      </div>
    </div>
  );
};

// MediaPipe drawing utilities
const drawConnectors = (ctx: CanvasRenderingContext2D, landmarks: any[], connections: any, style: any) => {
  ctx.strokeStyle = style.color;
  ctx.lineWidth = style.lineWidth;
  
  connections.forEach(([start, end]: [number, number]) => {
    ctx.beginPath();
    ctx.moveTo(landmarks[start].x * ctx.canvas.width, landmarks[start].y * ctx.canvas.height);
    ctx.lineTo(landmarks[end].x * ctx.canvas.width, landmarks[end].y * ctx.canvas.height);
    ctx.stroke();
  });
};

const drawLandmarks = (ctx: CanvasRenderingContext2D, landmarks: any[], style: any) => {
  ctx.fillStyle = style.color;
  landmarks.forEach((landmark: any) => {
    ctx.beginPath();
    ctx.arc(landmark.x * ctx.canvas.width, landmark.y * ctx.canvas.height, 4, 0, 2 * Math.PI);
    ctx.fill();
  });
};
