import React from 'react';
import { Dashboard } from './components/Dashboard';
import { useWebSocket } from './hooks/useWebSocket';
import './App.css';

function App() {
  // Initialize WebSocket with fallback to sample data
  useWebSocket('ws://localhost:8000/ws/intelligence');

  return <Dashboard />;
}

export default App;
