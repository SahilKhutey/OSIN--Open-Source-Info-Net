import { useState, useEffect } from 'react';

export const useIntelligenceData = () => {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    // Simulate real-time data fetching
    const interval = setInterval(() => {
      setData({
        timestamp: new Date(),
        threatLevel: Math.random() * 100,
        activeAlerts: Math.floor(Math.random() * 20),
        processedEvents: Math.floor(Math.random() * 1000)
      });
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return data;
};
