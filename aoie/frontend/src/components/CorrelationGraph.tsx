import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface Node extends d3.SimulationNodeDatum {
  id: string;
  group: number;
}

interface Link extends d3.SimulationLinkDatum<Node> {
  value: number;
}

const CorrelationGraph: React.FC = () => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    const width = 800;
    const height = 600;

    const data = {
      nodes: [
        { id: "AOIE-CORE", group: 1 },
        { id: "ENTITY-X", group: 2 },
        { id: "ENTITY-Y", group: 2 },
        { id: "LOCATION-A", group: 3 },
        { id: "EVENT-2026-001", group: 4 },
        { id: "SOURCE-REUTERS", group: 5 },
        { id: "SIGNAL-ALPHA", group: 6 }
      ],
      links: [
        { source: "AOIE-CORE", target: "EVENT-2026-001", value: 1 },
        { source: "EVENT-2026-001", target: "ENTITY-X", value: 5 },
        { source: "EVENT-2026-001", target: "ENTITY-Y", value: 5 },
        { source: "ENTITY-X", target: "LOCATION-A", value: 2 },
        { source: "ENTITY-Y", target: "LOCATION-A", value: 2 },
        { source: "SOURCE-REUTERS", target: "SIGNAL-ALPHA", value: 3 },
        { source: "SIGNAL-ALPHA", target: "EVENT-2026-001", value: 4 }
      ]
    };

    const svg = d3.select(svgRef.current)
      .attr("viewBox", `0 0 ${width} ${height}`)
      .style("background", "transparent");

    svg.selectAll("*").remove(); // Clear previous render

    const simulation = d3.forceSimulation<Node>(data.nodes)
      .force("link", d3.forceLink<Node, Link>(data.links).id(d => d.id).distance(100))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2));

    const link = svg.append("g")
      .attr("stroke", "#064e3b")
      .attr("stroke-opacity", 0.6)
      .selectAll("line")
      .data(data.links)
      .join("line")
      .attr("stroke-width", d => Math.sqrt(d.value));

    const node = svg.append("g")
      .selectAll("g")
      .data(data.nodes)
      .join("g")
      .call(d3.drag<SVGGElement, Node>()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended) as any);

    node.append("circle")
      .attr("r", 8)
      .attr("fill", d => ["#10b981", "#3b82f6", "#f59e0b", "#ef4444", "#a855f7", "#ec4899"][d.group - 1]);

    node.append("text")
      .text(d => d.id)
      .attr("x", 12)
      .attr("y", 4)
      .attr("fill", "#059669")
      .style("font-size", "10px")
      .style("font-family", "monospace")
      .style("pointer-events", "none");

    simulation.on("tick", () => {
      link
        .attr("x1", d => (d.source as Node).x!)
        .attr("y1", d => (d.source as Node).y!)
        .attr("x2", d => (d.target as Node).x!)
        .attr("y2", d => (d.target as Node).y!);

      node.attr("transform", d => `translate(${d.x},${d.y})`);
    });

    function dragstarted(event: any, d: Node) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event: any, d: Node) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event: any, d: Node) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }

    return () => simulation.stop();
  }, []);

  return (
    <div className="correlation-graph-container w-full h-full relative bg-green-950/5 border border-green-900 rounded-lg overflow-hidden shadow-inner">
      <div className="absolute top-4 left-4 flex gap-4 pointer-events-none">
        <div className="flex items-center gap-2 text-[10px] text-green-500/60 uppercase tracking-tighter">
          <span className="w-2 h-2 rounded-full bg-emerald-500"></span> Core
          <span className="w-2 h-2 rounded-full bg-blue-500"></span> Entity
          <span className="w-2 h-2 rounded-full bg-orange-500"></span> Location
        </div>
      </div>
      <svg ref={svgRef} className="w-full h-full" />
    </div>
  );
};

export default CorrelationGraph;
