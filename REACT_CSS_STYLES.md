# OSIN React Dashboard - Complete CSS Stylesheet

## File: src/App.css

```css
/* Global Styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --primary-color: #00ff00;
  --secondary-color: #0088ff;
  --danger-color: #ff0000;
  --warning-color: #ffaa00;
  --success-color: #00ff00;
  --background: #0a0a0a;
  --surface: #111111;
  --border: #333333;
  --text-primary: #00ff00;
  --text-secondary: #888888;
}

html, body {
  height: 100%;
  background-color: var(--background);
  color: var(--text-primary);
  font-family: 'Courier New', monospace;
  overflow-x: hidden;
}

body {
  margin: 0;
  padding: 0;
}

#root {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* App Container */
.app-container {
  min-height: 100vh;
  background: #000;
  display: flex;
  flex-direction: column;
}

/* Navigation */
.navigation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: var(--surface);
  border-bottom: 1px solid var(--primary-color);
  gap: 2rem;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.nav-brand h2 {
  margin: 0;
  color: var(--primary-color);
  text-shadow: 0 0 5px var(--primary-color);
  font-size: 1.5rem;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.status-dot.live {
  background: var(--primary-color);
  box-shadow: 0 0 10px var(--primary-color), 0 0 20px rgba(0, 255, 0, 0.5);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.nav-links {
  display: flex;
  gap: 2rem;
  flex: 1;
}

.nav-link {
  color: var(--primary-color);
  text-decoration: none;
  transition: all 0.2s;
  padding: 0.5rem 1rem;
  border-radius: 4px;
}

.nav-link:hover {
  color: #ffffff;
  text-shadow: 0 0 10px #ffffff;
  background: rgba(255, 255, 255, 0.1);
}

.nav-time {
  color: var(--text-secondary);
  font-size: 0.9rem;
  white-space: nowrap;
}

/* Dashboard Container */
.dashboard-container {
  padding: 2rem;
  flex: 1;
  overflow-y: auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.dashboard-header h1 {
  color: var(--primary-color);
  text-shadow: 0 0 10px var(--primary-color);
  font-size: 2rem;
  margin: 0;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(0, 255, 0, 0.1);
  border: 1px solid var(--primary-color);
  border-radius: 20px;
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
}

/* Dashboard Grid */
.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto auto auto;
  gap: 1rem;
  grid-template-areas:
    "livefeed alerts"
    "globe globe"
    "sources threat";
}

/* Panel Styles */
.panel {
  background: var(--surface);
  border: 1px solid;
  border-radius: 4px;
  padding: 1rem;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border);
}

.panel-header h2 {
  margin: 0;
  font-size: 1.1rem;
}

.text-green-400 {
  color: var(--primary-color);
}

.text-red-400 {
  color: var(--danger-color);
}

.text-blue-400 {
  color: var(--secondary-color);
}

.panel-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.event-count, .alert-count {
  background: rgba(0, 255, 0, 0.1);
  border: 1px solid var(--primary-color);
  border-radius: 12px;
  padding: 0.25rem 0.5rem;
  font-size: 0.8rem;
  color: var(--primary-color);
}

.btn-small {
  background: transparent;
  color: var(--primary-color);
  border: 1px solid var(--primary-color);
  border-radius: 4px;
  padding: 0.25rem 0.5rem;
  font-family: 'Courier New', monospace;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-small:hover {
  background: rgba(0, 255, 0, 0.1);
  text-shadow: 0 0 5px var(--primary-color);
}

.live-feed-panel {
  grid-area: livefeed;
  border-color: var(--primary-color);
}

.alerts-panel {
  grid-area: alerts;
  border-color: var(--danger-color);
}

.globe-panel {
  grid-area: globe;
  border-color: var(--secondary-color);
  height: 400px;
}

.source-panel {
  grid-area: sources;
  border-color: #ffffff;
}

.threat-panel {
  grid-area: threat;
  border-color: var(--warning-color);
}

/* Live Feed */
.live-feed-container {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.no-events {
  color: var(--text-secondary);
  text-align: center;
  padding: 2rem;
}

.event-item {
  padding: 0.75rem;
  background: rgba(0, 255, 0, 0.05);
  border-left: 3px solid var(--primary-color);
  border-radius: 2px;
  transition: all 0.2s;
  cursor: pointer;
}

.event-item:hover {
  background: rgba(0, 255, 0, 0.1);
  border-left-color: #ffffff;
}

.event-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.8rem;
}

.event-platform {
  color: var(--text-secondary);
}

.event-confidence {
  font-weight: bold;
}

.event-content {
  margin-bottom: 0.5rem;
  line-height: 1.4;
  font-size: 0.9rem;
}

.event-footer {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.event-time, .event-location {
  color: var(--text-secondary);
}

/* Alerts */
.alerts-container {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.no-alerts {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary);
}

.no-alerts-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.alert-item {
  padding: 0.75rem;
  margin-bottom: 0;
  border-radius: 4px;
  border: 1px solid;
}

.alert-item.critical {
  background: rgba(255, 0, 0, 0.15);
  border-color: var(--danger-color);
}

.alert-item.high {
  background: rgba(255, 85, 0, 0.15);
  border-color: #ff5500;
}

.alert-item.medium {
  background: rgba(255, 170, 0, 0.15);
  border-color: var(--warning-color);
}

.alert-item.low {
  background: rgba(0, 170, 255, 0.15);
  border-color: #00aaff;
}

.alert-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.8rem;
}

.alert-priority {
  font-weight: bold;
}

.alert-item.critical .alert-priority {
  color: var(--danger-color);
}

.alert-item.high .alert-priority {
  color: #ff5500;
}

.alert-item.medium .alert-priority {
  color: var(--warning-color);
}

.alert-item.low .alert-priority {
  color: #00aaff;
}

.alert-time {
  color: var(--text-secondary);
  font-size: 0.75rem;
}

.alert-message {
  margin-bottom: 0.5rem;
  line-height: 1.3;
}

.alert-source {
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
}

.acknowledge-btn {
  background: var(--primary-color);
  color: #000;
  border: none;
  padding: 0.3rem 0.6rem;
  border-radius: 3px;
  font-size: 0.75rem;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.2s;
}

.acknowledge-btn:hover {
  background: #ffffff;
  box-shadow: 0 0 10px var(--primary-color);
}

/* Globe */
.globe-container {
  width: 100%;
  height: 100%;
  position: relative;
}

/* Source Panel */
.source-panel-container {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.source-item {
  padding: 0.5rem;
  background: rgba(0, 255, 0, 0.05);
  border-radius: 3px;
}

.source-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.source-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.source-name {
  flex: 1;
  color: #ccc;
  font-size: 0.9rem;
}

.source-count {
  color: var(--primary-color);
  font-weight: bold;
  font-size: 0.9rem;
}

.source-bar {
  width: 100%;
  height: 4px;
  background: var(--border);
  border-radius: 2px;
  overflow: hidden;
}

.source-progress {
  height: 100%;
  transition: width 0.3s ease;
}

.source-total {
  display: flex;
  justify-content: space-between;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border);
  color: var(--primary-color);
  font-weight: bold;
}

.total-count {
  color: var(--primary-color);
}

/* Threat Bar */
.threat-bar-container {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.threat-level-text {
  font-weight: bold;
  text-align: center;
  font-size: 1.1rem;
}

.threat-bar {
  width: 100%;
  height: 20px;
  background: var(--border);
  border-radius: 10px;
  overflow: hidden;
}

.threat-progress {
  height: 100%;
  transition: width 0.3s ease;
  box-shadow: 0 0 10px currentColor;
}

.threat-metrics {
  display: flex;
  justify-content: space-around;
  gap: 1rem;
}

.metric {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}

.metric-label {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.metric-value {
  font-weight: bold;
  color: var(--primary-color);
  font-size: 1.1rem;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.9);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.2s;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-content {
  background: var(--surface);
  border: 1px solid var(--primary-color);
  border-radius: 8px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    transform: translateY(-50px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-header {
  padding: 1rem;
  border-bottom: 1px solid var(--primary-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  color: var(--primary-color);
  font-size: 1.3rem;
}

.modal-close {
  background: none;
  border: none;
  color: var(--primary-color);
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.modal-close:hover {
  color: #ffffff;
  text-shadow: 0 0 10px #ffffff;
}

.modal-body {
  padding: 1rem;
  overflow-y: auto;
  flex: 1;
}

.event-detail-section {
  margin-bottom: 1.5rem;
}

.event-detail-section h3 {
  color: var(--primary-color);
  margin-bottom: 0.5rem;
  border-bottom: 1px solid var(--border);
  padding-bottom: 0.25rem;
  font-size: 1rem;
}

.detail-item {
  display: flex;
  margin-bottom: 0.5rem;
  align-items: flex-start;
  gap: 1rem;
}

.detail-label {
  width: 120px;
  color: var(--text-secondary);
  font-weight: bold;
  flex-shrink: 0;
  font-size: 0.9rem;
}

.detail-value {
  flex: 1;
  color: var(--primary-color);
}

.text-content {
  white-space: pre-wrap;
  line-height: 1.5;
  background: rgba(0, 255, 0, 0.05);
  padding: 0.5rem;
  border-radius: 4px;
  margin-top: 0.25rem;
  border-left: 2px solid var(--primary-color);
}

.entities-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.entity-tag {
  background: rgba(0, 255, 0, 0.15);
  border: 1px solid var(--primary-color);
  border-radius: 12px;
  padding: 0.25rem 0.75rem;
  font-size: 0.8rem;
  color: var(--primary-color);
}

.engagement-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 1rem;
}

.modal-footer {
  padding: 1rem;
  border-top: 1px solid var(--primary-color);
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.btn-primary, .btn-secondary {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-family: 'Courier New', monospace;
  font-weight: bold;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--primary-color);
  color: #000;
  border: 1px solid var(--primary-color);
}

.btn-primary:hover {
  background: #ffffff;
  box-shadow: 0 0 15px var(--primary-color);
}

.btn-secondary {
  background: transparent;
  color: var(--primary-color);
  border: 1px solid var(--primary-color);
}

.btn-secondary:hover {
  background: rgba(0, 255, 0, 0.1);
  text-shadow: 0 0 5px var(--primary-color);
}

/* Enhanced Terminal */
.enhanced-terminal {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 60px);
  background: #000;
  color: var(--primary-color);
  font-family: 'Courier New', monospace;
}

.terminal-header {
  padding: 1rem;
  background: var(--surface);
  border-bottom: 1px solid var(--primary-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.terminal-header h2 {
  margin: 0;
  color: var(--primary-color);
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
  line-height: 1.4;
}

.terminal-line.error {
  color: var(--danger-color);
}

.command-line {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.prompt {
  color: var(--primary-color);
  font-weight: bold;
}

.command-text {
  color: var(--primary-color);
}

.output-line {
  color: var(--text-secondary);
  padding-left: 1.5rem;
}

.terminal-input-area {
  padding: 1rem;
  background: var(--surface);
  border-top: 1px solid var(--primary-color);
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.terminal-input {
  flex: 1;
  background: transparent;
  border: none;
  color: var(--primary-color);
  font-family: 'Courier New', monospace;
  outline: none;
  font-size: 1rem;
}

.terminal-input::placeholder {
  color: var(--text-secondary);
}

/* Scrollbars */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: var(--surface);
}

::-webkit-scrollbar-thumb {
  background: var(--primary-color);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #ffffff;
}

/* Page Content */
.page-content {
  padding: 2rem;
  color: var(--primary-color);
  text-align: center;
  font-size: 1.2rem;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
    grid-template-areas:
      "livefeed"
      "alerts"
      "globe"
      "sources"
      "threat";
  }

  .nav-links {
    gap: 1rem;
  }
}

@media (max-width: 768px) {
  .dashboard-container {
    padding: 1rem;
  }

  .dashboard-header {
    flex-direction: column;
    gap: 1rem;
  }

  .dashboard-header h1 {
    font-size: 1.5rem;
  }

  .navigation {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
  }

  .nav-links {
    width: 100%;
    justify-content: space-around;
  }

  .modal-content {
    width: 95%;
    max-height: 95vh;
  }

  .engagement-metrics {
    grid-template-columns: 1fr;
  }

  .threat-metrics {
    flex-direction: column;
    gap: 0.5rem;
  }
}

/* Animation Utilities */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes glow {
  0%, 100% {
    text-shadow: 0 0 5px var(--primary-color);
  }
  50% {
    text-shadow: 0 0 20px var(--primary-color);
  }
}

/* Utility Classes */
.text-center {
  text-align: center;
}

.flex {
  display: flex;
}

.flex-col {
  display: flex;
  flex-direction: column;
}

.gap-1 {
  gap: 0.5rem;
}

.gap-2 {
  gap: 1rem;
}

.p-4 {
  padding: 1rem;
}
```
