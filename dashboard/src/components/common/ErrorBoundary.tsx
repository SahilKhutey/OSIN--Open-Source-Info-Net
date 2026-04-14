import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children?: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('OSIN Uncaught Exception:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      if (this.fallback) {
          return this.fallback;
      }
      
      return (
        <div className="min-h-screen bg-black flex flex-col items-center justify-center p-8 font-mono">
          <div className="max-w-4xl w-full bg-gray-900 border-2 border-red-500 rounded-xl p-10 shadow-[0_0_50px_rgba(239,68,68,0.3)]">
            <h1 className="text-3xl font-black text-red-500 mb-6 flex items-center gap-4">
               <span className="animate-pulse">⚠️</span> SYSTEM FAILURE DETECTED
            </h1>
            
            <div className="bg-black/50 p-6 rounded border border-red-900/50 mb-8 overflow-auto max-h-[400px]">
              <p className="text-red-400 font-bold mb-2">ERROR_LOG_TRACE:</p>
              <pre className="text-xs text-red-600 font-light leading-relaxed">
                {this.state.error?.stack || this.state.error?.message}
              </pre>
            </div>

            <div className="space-y-4">
              <p className="text-gray-400 text-sm">
                The OSIN Intelligence Interface has encountered a critical runtime exception. 
                Possible causes include infrastructure desync, missing environment variables, 
                or incompatible browser dependencies.
              </p>
              
              <div className="flex gap-4">
                <button 
                  onClick={() => window.location.reload()}
                  className="px-6 py-3 bg-red-900/20 hover:bg-red-900/40 border border-red-500 text-red-500 font-bold text-xs uppercase tracking-widest transition-all rounded shadow-[0_0_15px_rgba(239,68,68,0.2)]"
                >
                  Initiate Hard Reload
                </button>
                <button 
                  onClick={() => window.location.href = '/'}
                  className="px-6 py-3 bg-gray-800 hover:bg-gray-700 border border-gray-600 text-gray-400 font-bold text-xs uppercase tracking-widest transition-all rounded"
                >
                  Return to Base
                </button>
              </div>
            </div>
          </div>
          
          <div className="mt-8 text-[10px] text-gray-700 uppercase tracking-[0.5em]">
             OSIN_CORE_RECOVERY_PROTOCOL_V8.0.0
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
