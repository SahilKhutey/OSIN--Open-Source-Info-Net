import ReconnectingWebSocket from 'reconnecting-websocket';
import { DashboardState, IntelligenceEvent, Alert, SourceStats } from '../types';

export class WebSocketService {
  private ws: ReconnectingWebSocket | null = null;
  private url: string;
  private listeners: Set<(data: Partial<DashboardState>) => void> = new Set();

  constructor(url: string) {
    this.url = url;
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new ReconnectingWebSocket(this.url);

        this.ws.onopen = () => {
          console.log('WebSocket connected');
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };

        this.ws.onclose = () => {
          console.log('WebSocket disconnected');
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  private handleMessage(message: any): void {
    const update: Partial<DashboardState> = {};

    if (message.type === 'event' && message.payload) {
      update.events = [message.payload];
    }

    if (message.type === 'alert' && message.payload) {
      update.alerts = [message.payload];
    }

    if (message.type === 'stats' && message.payload) {
      update.sourceStats = message.payload;
    }

    if (message.type === 'threat_level' && message.payload) {
      update.threatLevel = message.payload;
    }

    if (Object.keys(update).length > 0) {
      this.notifyListeners(update);
    }
  }

  subscribe(listener: (data: Partial<DashboardState>) => void): () => void {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  }

  private notifyListeners(update: Partial<DashboardState>): void {
    this.listeners.forEach((listener) => {
      listener(update);
    });
  }

  send(data: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}
