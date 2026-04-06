import { create } from 'zustand';
import { IntelligenceEvent } from '../types';

interface Cluster {
  center: {
    lat: number;
    lng: number;
  };
  events: IntelligenceEvent[];
  intensity: number;
}

interface HeatmapPoint {
  position: any;
  intensity: number;
  events: IntelligenceEvent[];
}

interface StoreState {
  events: IntelligenceEvent[];
  clusters: Cluster[];
  heatmap: HeatmapPoint[];
  addEvent: (event: IntelligenceEvent) => void;
  setClusters: (clusters: Cluster[]) => void;
  setHeatmap: (heatmap: HeatmapPoint[]) => void;
  clearEvents: () => void;
}

export const useStore = create<StoreState>((set) => ({
  events: [],
  clusters: [],
  heatmap: [],
  
  addEvent: (event) => set((state) => ({
    events: [event, ...state.events.slice(0, 99)]
  })),
  
  setClusters: (clusters) => set({ clusters }),
  
  setHeatmap: (heatmap) => set({ heatmap }),
  
  clearEvents: () => set({ 
    events: [], 
    clusters: [], 
    heatmap: [] 
  })
}));
