import React from 'react';
import { useStore } from '../store/useStore';
import '../styles/Alerts.css';

export const Alerts: React.FC = () => {
  const alerts = useStore((state) => state.alerts);
  const acknowledgeAlert = useStore((state) => state.acknowledgeAlert);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return '#ff0000';
      case 'high':
        return '#ff6600';
      case 'medium':
        return '#ffff00';
      case 'low':
        return '#00ff00';
      default:
        return '#00ffff';
    }
  };

  return (
    <div className="alerts-panel">
      <div className="alerts-header">
        <h3>[ACTIVE ALERTS]</h3>
        <span className="alert-count">{alerts.filter((a) => !a.acknowledged).length}</span>
      </div>

      <div className="alerts-list">
        {alerts.length === 0 ? (
          <div className="no-alerts">No active alerts</div>
        ) : (
          alerts.map((alert) => (
            <div
              key={alert.id}
              className={`alert-item ${alert.acknowledged ? 'acknowledged' : 'active'}`}
              style={{
                borderLeftColor: getSeverityColor(alert.severity),
              }}
            >
              <div className="alert-header-row">
                <span className="alert-title">{alert.title}</span>
                <span className={`alert-severity ${alert.severity}`}>
                  {alert.severity.toUpperCase()}
                </span>
              </div>
              <p className="alert-description">{alert.description}</p>
              <div className="alert-footer">
                <span className="alert-time">
                  {new Date(alert.timestamp).toLocaleTimeString()}
                </span>
                {!alert.acknowledged && (
                  <button
                    className="acknowledge-btn"
                    onClick={() => acknowledgeAlert(alert.id)}
                  >
                    ACK
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
