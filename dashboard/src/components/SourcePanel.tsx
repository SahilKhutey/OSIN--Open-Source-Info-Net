import React from 'react';
import { useStore } from '../store/useStore';
import '../styles/SourcePanel.css';

export const SourcePanel: React.FC = () => {
  const sourceStats = useStore((state) => state.sourceStats);

  const sources = [
    { name: 'Twitter', count: sourceStats.twitter, color: '#1DA1F2' },
    { name: 'Reddit', count: sourceStats.reddit, color: '#FF4500' },
    { name: 'YouTube', count: sourceStats.youtube, color: '#FF0000' },
    { name: 'News', count: sourceStats.news, color: '#FFB81C' },
    { name: 'Instagram', count: sourceStats.instagram || 0, color: '#E4405F' },
    { name: 'LinkedIn', count: sourceStats.linkedin || 0, color: '#0A66C2' },
  ];

  const total = sourceStats.total || sources.reduce((sum, s) => sum + s.count, 0);

  return (
    <div className="source-panel">
      <div className="source-header">
        <h3>[INFORMATION SOURCES]</h3>
        <span className="total-count">Total: {total}</span>
      </div>

      <div className="sources-grid">
        {sources.map((source) => {
          const percentage = total > 0 ? (source.count / total) * 100 : 0;
          return (
            <div key={source.name} className="source-item">
              <div className="source-name-row">
                <span className="source-name">{source.name}</span>
                <span className="source-count">{source.count}</span>
              </div>
              <div className="source-bar">
                <div
                  className="source-fill"
                  style={{
                    width: `${percentage}%`,
                    backgroundColor: source.color,
                  }}
                ></div>
              </div>
              <span className="source-percentage">{percentage.toFixed(1)}%</span>
            </div>
          );
        })}
      </div>

      <div className="source-footer">
        <p>Intelligence distribution across monitored sources</p>
        <p className="last-updated">
          Updated: {new Date(sourceStats.lastUpdated).toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
};
