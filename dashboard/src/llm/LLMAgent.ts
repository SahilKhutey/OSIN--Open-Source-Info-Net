import { useMemo, useCallback } from 'react';

/**
 * Lightweight browser-compatible EventEmitter
 */
class EventEmitter {
  private listeners: Record<string, Function[]> = {};

  on(event: string, listener: Function) {
    if (!this.listeners[event]) this.listeners[event] = [];
    this.listeners[event].push(listener);
    return this;
  }

  emit(event: string, ...args: any[]) {
    if (!this.listeners[event]) return false;
    this.listeners[event].forEach(listener => listener(...args));
    return true;
  }
}

interface LLMResponse {
  response: string;
  intent: string;
  confidence: number;
  actions?: string[];
  parameters?: Record<string, any>;
}

/**
 * OSINT XR Intelligence Agent
 * Manages conversational state and interfaces with the LLM backend.
 */
class LLMAgent extends EventEmitter {
  private baseUrl: string;
  private history: Array<{ role: 'user' | 'assistant' | 'system'; content: string }>;

  constructor(baseUrl: string = 'http://localhost:8001') {
    super();
    this.baseUrl = baseUrl;
    this.history = [];
  }

  async processQuery(text: string, context: Record<string, any> = {}): Promise<LLMResponse> {
    try {
      this.history.push({ role: 'user', content: text });

      const response = await fetch(`${this.baseUrl}/agent`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text,
          history: this.history.slice(-12), // Maintain short-term context window
          context
        }),
      });

      if (!response.ok) throw new Error(`Agent Connection Error: ${response.status}`);

      const data: LLMResponse = await response.json();
      
      this.history.push({ role: 'assistant', content: data.response });

      // Emit events for internal system reactive logic
      this.emit('response_received', data);
      if (data.actions) {
        data.actions.forEach(action => this.emit('action_triggered', { action, params: data.parameters }));
      }

      return data;
    } catch (error) {
      console.error('LLM Agent failure:', error);
      throw error;
    }
  }

  clearMemory(): void {
    this.history = [];
  }

  getConversation(): any[] {
    return [...this.history];
  }
}

/**
 * React Hook for AI integration
 */
export const useLLMAgent = (url?: string) => {
  const agent = useMemo(() => new LLMAgent(url), [url]);

  const askAgent = useCallback(async (query: string, context?: any) => {
    return await agent.processQuery(query, context);
  }, [agent]);

  const resetAgent = useCallback(() => {
    agent.clearMemory();
  }, [agent]);

  return {
    askAgent,
    resetAgent,
    agentInstance: agent,
    getHistory: agent.getConversation.bind(agent)
  };
};
