import React from 'react';
import { useStore } from '../store/useStore';
import '../styles/LiveFeed.css';

export const LiveFeed: React.FC = () => {
  const events = useStore((state) => state.events.slice(0, 10));

  const getSeverityClass = (severity: string) => {
    return `severity-${severity.toLowerCase()}`;
  };

  const formatTime = (isoString: string) => {
    const date = new Date(isoString);
    return date.toLocaleTimeString();
  };

  return (
    <div className="live-feed">
      <div className="feed-header">
        <h3>[LIVE INTELLIGENCE FEED]</h3>
        <span className="event-count">{events.length} Events</span>
      </div>

      <div className="feed-container">
        {events.length === 0 ? (
          <div className="no-events">
            <span>> AWAITING SIGNAL STREAM...</span>
          </div>
        ) : (
          <div className="feed-items">
            {events.map((event) => (
              <div key={event.id} className={`feed-item ${getSeverityClass(event.severity)}`}>
                <div className="item-header">
                  <span className="timestamp">{formatTime(event.timestamp)}</span>
                  <span className={`severity-badge ${getSeverityClass(event.severity)}`}>
                    {event.severity.toUpperCase()}
                  </span>
                </div>
                <div className="item-content">
                  <p className="source">[{event.source}]</p>
                  <p className="text">{event.content.substring(0, 100)}...</p>
                  {event.location && (
                    <span className="location">📍 {event.location.country}</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
