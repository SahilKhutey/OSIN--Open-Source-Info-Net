/* OSIN 3D DASHBOARD - CSS STYLES
   Copy each section to the appropriate CSS file in dashboard/src/styles/
*/

/* ============================================
   FILE: src/App.css
   Main application styles
   ============================================ */

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  width: 100%;
  height: 100%;
}

body {
  background-color: #0a0a0a;
  color: #00ff00;
  font-family: 'Courier New', monospace;
  overflow-x: hidden;
}

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
  background: #111;
  border-bottom: 2px solid #00ff00;
  box-shadow: 0 0 10px rgba(0, 255, 0, 0.2);
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.nav-brand h2 {
  color: #00ff00;
  text-shadow: 0 0 10px #00ff00;
  font-size: 1.5rem;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #333;
}

.status-dot.live {
  background: #00ff00;
  box-shadow: 0 0 8px #00ff00;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.nav-links {
  display: flex;
  gap: 3rem;
}

.nav-link {
  color: #00ff00;
  text-decoration: none;
  font-size: 0.95rem;
  transition: all 0.3s;
  border-bottom: 2px solid transparent;
}

.nav-link:hover {
  color: #ffffff;
  text-shadow: 0 0 10px #ffffff;
  border-bottom-color: #00ff00;
}

.nav-time {
  color: #666;
  font-size: 0.85rem;
  font-family: monospace;
}

/* Dashboard */
.dashboard-container {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #00ff00;
}

.dashboard-header h1 {
  color: #00ff00;
  text-shadow: 0 0 15px #00ff00;
  font-size: 2rem;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #00ff00;
  font-weight: bold;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto auto auto;
  gap: 1.5rem;
  grid-template-areas:
    "livefeed alerts"
    "globe globe"
    "sources threat";
}

.panel {
  background: #111;
  border: 1px solid #00ff00;
  border-radius: 4px;
  padding: 1.5rem;
  overflow: hidden;
  box-shadow: 0 0 10px rgba(0, 255, 0, 0.1);
  transition: all 0.3s;
}

.panel:hover {
  box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);
}

.panel h2 {
  color: #00ff00;
  font-size: 1rem;
  margin-bottom: 1rem;
  text-transform: uppercase;
  letter-spacing: 2px;
  text-shadow: 0 0 5px #00ff00;
}

.live-feed-panel {
  grid-area: livefeed;
}

.alerts-panel {
  grid-area: alerts;
  border-color: #ff5500;
}

.alerts-panel h2 {
  color: #ff5500;
  text-shadow: 0 0 5px #ff5500;
}

.globe-panel {
  grid-area: globe;
  min-height: 450px;
  border-color: #0088ff;
}

.globe-panel h2 {
  color: #0088ff;
  text-shadow: 0 0 5px #0088ff;
}

.source-panel {
  grid-area: sources;
  border-color: #ffaa00;
}

.source-panel h2 {
  color: #ffaa00;
  text-shadow: 0 0 5px #ffaa00;
}

.threat-panel {
  grid-area: threat;
  border-color: #ff0000;
}

.threat-panel h2 {
  color: #ff0000;
  text-shadow: 0 0 5px #ff0000;
}

.analytics-page {
  padding: 2rem;
  color: #00ff00;
}

/* Scrollbars */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #1a1a1a;
}

::-webkit-scrollbar-thumb {
  background: #00ff00;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #00cc00;
}

/* Responsive */
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


/* ============================================
   FILE: src/styles/live-feed.css
   ============================================ */

.live-feed-container {
  max-height: 350px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.no-events {
  text-align: center;
  padding: 2rem;
  color: #666;
  font-style: italic;
}

.event-item {
  padding: 0.75rem;
  background: #1a1a1a;
  border-left: 3px solid #00ff00;
  border-radius: 2px;
  transition: all 0.2s;
  cursor: pointer;
}

.event-item:hover {
  background: #222;
  border-left-color: #00cc00;
  box-shadow: 0 0 5px rgba(0, 255, 0, 0.1);
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.8rem;
}

.event-platform {
  color: #888;
  text-transform: uppercase;
  font-weight: bold;
}

.event-confidence {
  font-weight: bold;
  padding: 0 0.5rem;
}

.event-content {
  margin-bottom: 0.5rem;
  line-height: 1.4;
  color: #ccc;
  font-size: 0.9rem;
}

.event-footer {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: #666;
}

.event-time {
  color: #555;
}

.event-location {
  color: #888;
}


/* ============================================
   FILE: src/styles/alerts.css
   ============================================ */

.alerts-container {
  max-height: 350px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.no-alerts {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.no-alerts-icon {
  font-size: 2.5rem;
  margin-bottom: 0.75rem;
}

.no-alerts-text {
  font-style: italic;
}

.alert-item {
  padding: 0.75rem;
  border-radius: 4px;
  border: 1px solid;
  transition: all 0.2s;
}

.alert-item.high {
  background: rgba(255, 0, 0, 0.15);
  border-color: #ff0000;
}

.alert-item.medium {
  background: rgba(255, 170, 0, 0.15);
  border-color: #ffaa00;
}

.alert-item.low {
  background: rgba(0, 170, 255, 0.15);
  border-color: #00aaff;
}

.alert-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.8rem;
}

.alert-priority {
  font-weight: bold;
  text-transform: uppercase;
}

.alert-item.high .alert-priority {
  color: #ff0000;
}

.alert-item.medium .alert-priority {
  color: #ffaa00;
}

.alert-item.low .alert-priority {
  color: #00aaff;
}

.alert-time {
  color: #888;
  font-size: 0.75rem;
}

.alert-message {
  margin-bottom: 0.5rem;
  color: #ccc;
  line-height: 1.3;
}

.alert-source {
  font-size: 0.75rem;
  color: #666;
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px dashed rgba(0, 255, 0, 0.2);
}


/* ============================================
   FILE: src/styles/threat-bar.css
   ============================================ */

.threat-bar-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.threat-level-text {
  font-weight: bold;
  text-align: center;
  font-size: 1.1rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.threat-bar {
  width: 100%;
  height: 24px;
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.5);
}

.threat-progress {
  height: 100%;
  transition: width 0.3s ease, background-color 0.3s ease;
  border-radius: 12px;
}

.threat-metrics {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-top: 0.5rem;
}

.metric {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.metric-label {
  font-size: 0.8rem;
  color: #888;
  text-transform: uppercase;
}

.metric-value {
  font-weight: bold;
  color: #00ff00;
  font-size: 1.2rem;
}


/* ============================================
   FILE: src/styles/source-panel.css
   ============================================ */

.source-panel-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.source-item {
  padding: 0.75rem;
  background: #1a1a1a;
  border-radius: 3px;
  border: 1px solid #333;
}

.source-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.source-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.source-name {
  flex: 1;
  color: #ccc;
  font-weight: bold;
  text-transform: uppercase;
  font-size: 0.9rem;
}

.source-count {
  color: #00ff00;
  font-weight: bold;
  font-size: 0.95rem;
}

.source-bar {
  width: 100%;
  height: 6px;
  background: #333;
  border-radius: 3px;
  overflow: hidden;
}

.source-progress {
  height: 100%;
  transition: width 0.3s ease;
  border-radius: 3px;
}

.source-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #333;
  color: #00ff00;
  font-weight: bold;
  text-transform: uppercase;
}

.total-count {
  font-size: 1.2rem;
}
