import React, { useState, useEffect, useRef } from 'react';
import ForceGraph3D from 'react-force-graph-3d';
import * as THREE from 'three';
import './GraphVisualization.css';

interface GraphVisualizationProps {
  initialEntityId?: string;
  onClose: () => void;
}

export const GraphVisualization: React.FC<GraphVisualizationProps> = ({ 
  initialEntityId, 
  onClose 
}) => {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [loading, setLoading] = useState(false);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const fgRef = useRef<any>();

  const fetchSubgraph = async (entityId?: string) => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8020/query/subgraph', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ entity_id: entityId, depth: 2 })
      });
      
      const data = await response.json();
      
      // Transform OSIN Graph Data to ForceGraph Data
      const nodes = (data.entities || []).map((e: any) => ({
        id: e.id,
        name: e.properties.name || e.properties.domain || e.properties.ip || e.id,
        type: e.type,
        properties: e.properties,
        color: getNodeColor(e.type)
      }));

      const links = (data.relationships || []).map((r: any) => ({
        source: r.source_id,
        target: r.target_id,
        relationship: r.type,
        confidence: r.confidence
      }));

      setGraphData({ nodes, links });
      if (fgRef.current) {
        fgRef.current.d3ReheatSimulation();
      }
    } catch (err) {
      console.error('Failed to fetch subgraph:', err);
    } finally {
      setLoading(false);
    }
  };

  const getNodeColor = (type: string) => {
    const colors: any = {
      'person': '#ff6b6b',
      'location': '#4ecdc4',
      'domain': '#45b7d1',
      'ip_address': '#f9ca24',
      'threat_signal': '#eb4d4b',
      'event': '#a29bfe'
    };
    return colors[type] || '#dfe6e9';
  };

  useEffect(() => {
    fetchSubgraph(initialEntityId);
  }, [initialEntityId]);

  return (
    <div className="graph-viz-overlay">
      <div className="graph-viz-container">
        <div className="graph-viz-header">
          <div className="title-stack">
            <h3>🔗 Unified Graph Reasoning</h3>
            <span>Cross-Source Entity Fusion | Situational Logic | v3.6.0</span>
          </div>
          <div className="controls">
            <button className="refresh-btn" onClick={() => fetchSubgraph(initialEntityId)}>↻</button>
            <button className="close-btn" onClick={onClose}>×</button>
          </div>
        </div>

        <div className="graph-viz-body">
          {loading && <div className="loader">Fusing Neural Connections...</div>}
          <ForceGraph3D
            ref={fgRef}
            graphData={graphData}
            backgroundColor="#000000"
            nodeLabel={(node: any) => `${node.type.toUpperCase()}: ${node.name}`}
            nodeRelSize={6}
            nodeColor={(node: any) => node.color}
            linkColor={() => '#444'}
            linkDirectionalArrowLength={3.5}
            linkDirectionalArrowRelPos={1}
            onNodeClick={(node) => setSelectedNode(node)}
            nodeThreeObjectExtend={true}
            nodeThreeObject={(node: any) => {
              // Custom labels or sprites can go here
              return false;
            }}
          />

          {selectedNode && (
            <div className="node-inspector">
              <div className="inspector-header">
                <h4>{selectedNode.type.toUpperCase()} Data</h4>
                <button onClick={() => setSelectedNode(null)}>×</button>
              </div>
              <div className="inspector-content">
                <div className="prop-row">
                  <span className="key">ID:</span>
                  <span className="val">{selectedNode.id}</span>
                </div>
                {Object.entries(selectedNode.properties).map(([k, v]: [string, any]) => (
                  <div className="prop-row" key={k}>
                    <span className="key">{k}:</span>
                    <span className="val">{typeof v === 'object' ? JSON.stringify(v) : String(v)}</span>
                  </div>
                ))}
              </div>
              <button 
                className="expand-btn" 
                onClick={() => fetchSubgraph(selectedNode.id)}
              >
                Expand Reasoning Path
              </button>
            </div>
          )}
        </div>
        
        <div className="graph-viz-footer">
          Centrality: Active | Semantic Similarity: v2.1 | Connected Components: Dynamic
        </div>
      </div>
    </div>
  );
};

export default GraphVisualization;
