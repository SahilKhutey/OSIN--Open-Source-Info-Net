/* Advanced CSS Styles - Terminal, Agents, Heatmap */

/* Enhanced Terminal */
.enhanced-terminal {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #000;
  color: #00ff00;
  font-family: 'Courier New', monospace;
}

.terminal-header {
  padding: 1rem;
  background: #111;
  border-bottom: 1px solid #00ff00;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.terminal-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.terminal-output {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
  background: #000;
}

.terminal-line {
  margin-bottom: 0.5rem;
}

.command-line {
  display: flex;
  align-items: center;
}

.prompt {
  color: #00ff00;
  margin-right: 0.5rem;
  font-weight: bold;
}

.command-text {
  color: #ffffff;
}

.output-line {
  color: #00ff00;
  white-space: pre-wrap;
}

.output-line.error {
  color: #ff5500;
}

.terminal-input-area {
  display: flex;
  align-items: center;
  padding: 1rem;
  background: #111;
  border-top: 1px solid #00ff00;
}

.terminal-input {
  flex: 1;
  background: #000;
  color: #00ff00;
  border: 1px solid #00ff00;
  padding: 0.5rem;
  font-family: 'Courier New', monospace;
  outline: none;
}

/* Agent Overlay */
.agent-overlay {
  background: rgba(17, 17, 17, 0.9);
  border: 1px solid #00ff00;
  border-radius: 4px;
  padding: 1rem;
  margin-top: 1rem;
}

.agent-overlay h3 {
  color: #00ff00;
  margin-top: 0;
  border-bottom: 1px solid #333;
  padding-bottom: 0.5rem;
}

.agents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.agent-card {
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 4px;
  padding: 1rem;
  cursor: pointer;
  transition: border-color 0.2s;
}

.agent-card:hover {
  border-color: #00ff00;
}

.agent-card.active {
  border-color: #00ff00;
  box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
}

.agent-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.agent-name {
  font-weight: bold;
  color: #00ff00;
}

.agent-status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.agent-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.agent-metric {
  display: flex;
  justify-content: space-between;
}

.metric-label {
  color: #888;
}

.metric-value {
  color: #00ff00;
  font-weight: bold;
}

/* Heatmap Mode */
.heatmap-mode .globe-container {
  background: linear-gradient(135deg, #000000 0%, #1a1a2e 100%);
}

/* Timeline Replay */
.timeline-replay {
  background: #111;
  border: 1px solid #00ff00;
  border-radius: 4px;
  padding: 1rem;
  margin-top: 1rem;
}

.timeline-controls {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.play-pause-btn, .reset-btn {
  background: #00ff00;
  color: #000;
  border: none;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.2s;
}

.play-pause-btn:hover, .reset-btn:hover {
  background: #ffffff;
  box-shadow: 0 0 10px #00ff00;
}

.speed-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.speed-control select {
  background: #000;
  color: #00ff00;
  border: 1px solid #00ff00;
  border-radius: 4px;
  padding: 0.25rem 0.5rem;
  font-family: 'Courier New', monospace;
}

.time-display {
  text-align: center;
  margin-bottom: 0.5rem;
  color: #00ff00;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

.timeline-slider {
  width: 100%;
  margin-bottom: 1rem;
}

.event-counter {
  text-align: center;
  color: #00ff00;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.timeline-events {
  max-height: 200px;
  overflow-y: auto;
}

.timeline-event {
  padding: 0.5rem;
  border-bottom: 1px solid #333;
  cursor: pointer;
  transition: background 0.2s;
}

.timeline-event:hover {
  background: rgba(0, 255, 0, 0.1);
}

.event-time {
  color: #888;
  font-size: 0.8rem;
  margin-right: 0.5rem;
}

.event-platform {
  color: #00ff00;
  font-weight: bold;
  margin-right: 0.5rem;
}

.event-text {
  color: #ccc;
  font-size: 0.85rem;
}

/* Page Content */
.page-content {
  padding: 2rem;
  color: #00ff00;
  font-family: 'Courier New', monospace;
}

/* Animation Effects */
@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

@keyframes glow {
  0%, 100% {
    text-shadow: 0 0 5px #00ff00;
  }
  50% {
    text-shadow: 0 0 20px #00ff00;
  }
}

.status-dot.live {
  animation: pulse 2s infinite;
}

.status-dot.offline {
  background-color: #888;
}

/* Scrollbar Styles */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #111;
}

::-webkit-scrollbar-thumb {
  background: #00ff00;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #00cc00;
}

/* Focus Styles for Accessibility */
button:focus, a:focus, input:focus {
  outline: 2px solid #00ff00;
  outline-offset: 2px;
}

/* Responsive Improvements */
@media (max-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: 1fr 1fr;
    grid-template-areas:
      "livefeed alerts"
      "globe globe"
      "sources threat";
  }
  
  .agents-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
    grid-template-areas:
      "livefeed"
      "alerts"
      "globe"
      "sources"
      "threat";
  }
  
  .navigation {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
  }
  
  .nav-links {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .agents-grid {
    grid-template-columns: 1fr;
  }
  
  .timeline-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .play-pause-btn, .reset-btn {
    width: 100%;
  }
}
