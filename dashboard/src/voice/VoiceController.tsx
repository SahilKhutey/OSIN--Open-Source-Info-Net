import React, { useEffect, useState, useCallback, useRef } from 'react';

interface VoiceCommand {
  text: string;
  intent: string;
  confidence: number;
  timestamp: Date;
}

interface VoiceControllerProps {
  onCommand: (command: VoiceCommand) => void;
  onStatusChange: (status: 'ready' | 'listening' | 'processing' | 'error' | 'unsupported') => void;
}

export const VoiceController: React.FC<VoiceControllerProps> = ({
  onCommand,
  onStatusChange
}) => {
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      console.warn('Speech recognition not supported in this browser.');
      onStatusChange('unsupported');
      return;
    }

    const recognizer = new SpeechRecognition();
    recognizer.continuous = true;
    recognizer.lang = 'en-US';
    recognizer.interimResults = false;
    recognizer.maxAlternatives = 1;

    recognizer.onstart = () => {
      setIsListening(true);
      onStatusChange('listening');
    };

    recognizer.onend = () => {
      setIsListening(false);
      onStatusChange('ready');
    };

    recognizer.onresult = async (event: any) => {
      const transcript = event.results[event.results.length - 1][0].transcript.trim();
      const confidence = event.results[event.results.length - 1][0].confidence;
      
      onStatusChange('processing');
      console.log('Voice Command Input:', transcript);

      try {
        const intentResult = await processVoiceIntent(transcript);
        
        onCommand({
          text: transcript,
          intent: intentResult.action,
          confidence,
          timestamp: new Date()
        });
        
        showVisualFeedback(transcript, intentResult.action);
        
      } catch (error) {
        console.error('Intent processing failure:', error);
        onStatusChange('error');
      }
    };

    recognizer.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      onStatusChange('error');
    };

    recognitionRef.current = recognizer;
  }, [onCommand, onStatusChange]);

  const toggleListening = useCallback(() => {
    if (!recognitionRef.current) return;

    if (isListening) {
      recognitionRef.current.stop();
    } else {
      recognitionRef.current.start();
    }
  }, [isListening]);

  const processVoiceIntent = async (text: string): Promise<{ action: string }> => {
    const response = await fetch('http://localhost:8001/voice-intent', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);
    return await response.json();
  };

  const showVisualFeedback = (text: string, intent: string) => {
    const el = document.createElement('div');
    el.className = 'fixed top-1/4 left-1/2 -translate-x-1/2 bg-black/80 border-2 border-cyan-500 p-6 rounded-2xl text-center z-[9999] backdrop-blur-xl animate-bounce-short';
    el.innerHTML = `
      <div class="text-cyan-400 font-mono text-lg mb-2">🎙️ "${text}"</div>
      <div class="text-white font-mono text-sm opacity-60 uppercase tracking-widest">EXECUTING: ${intent}</div>
    `;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 4000);
  };

  return (
    <div className="fixed bottom-8 right-24 z-50 group">
      <div className="absolute -top-12 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity bg-black/60 text-cyan-400 text-[10px] py-1 px-3 rounded border border-cyan-500/30 whitespace-nowrap uppercase tracking-tighter">
        {isListening ? 'STOP ACOUSTIVE MONITORING' : 'INITIATE VOICE COMMAND'}
      </div>
      
      <button
        onClick={toggleListening}
        className={`w-14 h-14 rounded-full flex items-center justify-center transition-all shadow-2xl ${
          isListening 
            ? 'bg-red-600/80 shadow-red-500/40 animate-pulse' 
            : 'bg-cyan-600/80 shadow-cyan-500/40 hover:scale-110 active:scale-95'
        }`}
      >
        <span className="text-2xl">{isListening ? '🎙️' : '🎤'}</span>
      </button>
      
      {isListening && (
        <div className="absolute -inset-2 rounded-full border-2 border-cyan-500/20 animate-ping"></div>
      )}
    </div>
  );
};
