import React from 'react';
import { AdvancedGlobe } from './AdvancedGlobe';
import { useStore } from '../store/useStore';
import '../styles/Dashboard.css';

export const Dashboard: React.FC = () => {
  const { events, clusters, heatmap } = useStore();

  const recentEvents = events.slice(0, 10);
  const criticalEvents = events.filter(e => e.severity === 'critical');
  const topSources = Array.from(new Set(events.map(e => e.source)))
    .slice(0, 6)
    .map(source => ({
      source,
      count: events.filter(e => e.source === source).length
    }))
    .sort((a, b) => b.count - a.count);

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>OSIN ADVANCED INTELLIGENCE DASHBOARD</h1>
        <div className="header-stats">
          <div className="stat-item">
            <span className="stat-label">Events</span>
            <span className="stat-value">{events.length}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Clusters</span>
            <span className="stat-value">{clusters.length}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Critical</span>
            <span className="stat-value critical">{criticalEvents.length}</span>
          </div>
        </div>
      </header>

      <div className="dashboard-grid">
        {/* Main visualization */}
        <div className="main-section">
          <div className="globe-container">
            <AdvancedGlobe />
          </div>
        </div>

        {/* Left column: Cluster Analysis */}
        <div className="left-column">
          <div className="panel cluster-analysis">
            <div className="panel-header">
              <h2>CLUSTER ANALYSIS</h2>
              <span className="panel-badge">{clusters.length}</span>
            </div>
            <div className="panel-content">
              {clusters.length === 0 ? (
                <div className="empty-state">No clusters detected</div>
              ) : (
                <div className="cluster-list">
                  {clusters.map((cluster, idx) => (
                    <div key={idx} className="cluster-item">
                      <div className="cluster-header">
                        <span className="cluster-id">Cluster #{idx + 1}</span>
                        <span className="cluster-count">{cluster.events.length} events</span>
                      </div>
                      <div className="cluster-location">
                        {cluster.center.lat.toFixed(2)}°, {cluster.center.lng.toFixed(2)}°
                      </div>
                      <div className="cluster-bar">
                        <div 
                          className="cluster-fill" 
                          style={{ width: `${(cluster.intensity / 10) * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Activity Hotspots */}
          <div className="panel activity-hotspots">
            <div className="panel-header">
              <h2>ACTIVITY HOTSPOTS</h2>
              <span className="panel-badge">{heatmap.length}</span>
            </div>
            <div className="panel-content">
              {heatmap.length === 0 ? (
                <div className="empty-state">No hotspots detected</div>
              ) : (
                <div className="hotspot-list">
                  {heatmap.slice(0, 5).map((h, idx) => (
                    <div key={idx} className="hotspot-item">
                      <div className="hotspot-intensity">
                        {(h.intensity * 100).toFixed(0)}%
                      </div>
                      <div className="hotspot-events">
                        {h.events.length} event{h.events.length !== 1 ? 's' : ''}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right column: Recent Events & Sources */}
        <div className="right-column">
          {/* Top Sources */}
          <div className="panel top-sources">
            <div className="panel-header">
              <h2>TOP SOURCES</h2>
            </div>
            <div className="panel-content">
              {topSources.length === 0 ? (
                <div className="empty-state">No events</div>
              ) : (
                <div className="source-list">
                  {topSources.map((s, idx) => (
                    <div key={idx} className="source-item">
                      <div className="source-name">{s.source}</div>
                      <div className="source-count">{s.count}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Recent Events */}
          <div className="panel recent-events">
            <div className="panel-header">
              <h2>RECENT EVENTS</h2>
              <span className="panel-badge">{recentEvents.length}</span>
            </div>
            <div className="panel-content events-scroll">
              {recentEvents.length === 0 ? (
                <div className="empty-state">Waiting for events...</div>
              ) : (
                <div className="event-list">
                  {recentEvents.map((event) => (
                    <div key={event.id} className={`event-item severity-${event.severity}`}>
                      <div className="event-header">
                        <span className="event-source">{event.source}</span>
                        <span className={`event-severity ${event.severity}`}>
                          {event.severity.toUpperCase()}
                        </span>
                      </div>
                      <div className="event-content">
                        {event.content.substring(0, 80)}...
                      </div>
                      <div className="event-meta">
                        {event.location && (
                          <span className="event-location">
                            📍 {event.location.city || 'Unknown'}
                          </span>
                        )}
                        {event.confidence && (
                          <span className="event-confidence">
                            ✓ {(event.confidence * 100).toFixed(0)}%
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
