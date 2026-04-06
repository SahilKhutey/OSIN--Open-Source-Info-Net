import { useEffect, useRef } from 'react';
import { useStore } from '../store/useStore';
import { IntelligenceEvent } from '../types';

const generateSampleEvent = (): IntelligenceEvent => {
  const sources = ['Twitter', 'Reddit', 'YouTube', 'News', 'Instagram', 'LinkedIn'];
  const severities: Array<'low' | 'medium' | 'high' | 'critical'> = ['low', 'medium', 'high', 'critical'];
  const lat = Math.random() * 180 - 90;
  const lng = Math.random() * 360 - 180;

  const eventTemplates = [
    'Intelligence report indicates unusual activity in the region',
    'Social media monitoring detected spike in discussions',
    'Automated system identified patterns matching threat indicators',
    'News aggregation flagged significant developments',
    'Real-time analysis suggests emerging trend',
    'Cross-platform data correlation revealed connections',
    'Event tracking system logged notable occurrence',
    'Sentiment analysis indicates changing regional dynamics'
  ];

  const eventText = eventTemplates[Math.floor(Math.random() * eventTemplates.length)];

  return {
    id: `event-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    timestamp: Date.now(),
    source: sources[Math.floor(Math.random() * sources.length)],
    type: 'intelligence',
    severity: severities[Math.floor(Math.random() * severities.length)],
    content: eventText,
    text: eventText,
    platform: sources[Math.floor(Math.random() * sources.length)],
    confidence: Math.random() * 0.5 + 0.5,
    location: {
      lat,
      lng,
      lon: lng,
      country: 'Sample Country',
      city: 'Sample City'
    }
  };
};

export const useWebSocket = (url?: string) => {
  const { addEvent } = useStore();
  const wsRef = useRef<WebSocket | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    // If URL provided, try to connect to WebSocket
    if (url) {
      try {
        wsRef.current = new WebSocket(url);

        wsRef.current.onopen = () => {
          console.log('WebSocket connected');
        };

        wsRef.current.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.events && Array.isArray(data.events)) {
              data.events.forEach((evt: IntelligenceEvent) => addEvent(evt));
            }
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };

        wsRef.current.onerror = (error) => {
          console.error('WebSocket error:', error);
        };

        wsRef.current.onclose = () => {
          console.log('WebSocket disconnected');
        };
      } catch (error) {
        console.error('Failed to connect to WebSocket:', error);
      }
    }

    // Fallback: Generate sample events for demo
    intervalRef.current = setInterval(() => {
      if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
        addEvent(generateSampleEvent());
      }
    }, 2000);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [url, addEvent]);

  return {
    send: (data: any) => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify(data));
      }
    },
    disconnect: () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    },
  };
};
