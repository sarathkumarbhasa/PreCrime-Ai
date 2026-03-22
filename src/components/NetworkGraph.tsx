import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';

export default function NetworkGraph() {
  const svgRef = useRef<SVGSVGElement>(null);
  const [graphData, setGraphData] = useState<{nodes: any[], edges: any[]} | null>(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/graph')
      .then(r => r.json())
      .then(data => {
        console.log('Graph data:', data);
        setGraphData(data);
      })
      .catch(err => console.error("Error fetching graph data:", err));
  }, []);

  useEffect(() => {
    if (!graphData || !svgRef.current) return;

    const width = svgRef.current.clientWidth || 800;
    const height = svgRef.current.clientHeight || 500;

    d3.select(svgRef.current).selectAll('*').remove();

    const svg = d3.select(svgRef.current)
      .attr('width', '100%')
      .attr('height', '100%')
      .call(d3.zoom().on('zoom', (event) => {
        g.attr('transform', event.transform);
      }));

    const g = svg.append('g');

    const getColor = (score: number) => {
      if (score >= 81) return '#FF4444';   // red
      if (score >= 66) return '#FF6B35';   // orange  
      if (score >= 41) return '#FFD700';   // yellow
      return '#44FF88';                    // green
    };

    const nodes = graphData.nodes.map(d => ({ ...d }));
    const edges = graphData.edges.map(d => ({ ...d }));

    const simulation = d3.forceSimulation(nodes as d3.SimulationNodeDatum[])
      .force('link', d3.forceLink(edges).id((d: any) => d.id).distance(80))
      .force('charge', d3.forceManyBody().strength(-200))
      .force('center', d3.forceCenter(width/2, height/2))
      .force('collision', d3.forceCollide().radius(25));

    const link = g.append('g')
      .selectAll('line')
      .data(edges)
      .join('line')
      .attr('stroke', '#334155')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', (d: any) => Math.sqrt(d.weight || 1));

    const node = g.append('g')
      .selectAll('circle')
      .data(nodes)
      .join('circle')
      .attr('r', 15)
      .attr('fill', (d: any) => getColor(d.heat_score || 0))
      .attr('stroke', '#000')
      .attr('stroke-width', 1.5)
      .style('cursor', 'pointer')
      .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended) as any);

    const label = g.append('g')
      .selectAll('text')
      .data(nodes)
      .join('text')
      .attr('dy', 4)
      .attr('dx', 20)
      .text((d: any) => d.label)
      .attr('font-size', '10px')
      .attr('fill', '#94a3b8')
      .attr('font-family', 'monospace');

    node.append('title')
      .text((d: any) => `${d.id}\nHeat: ${d.heat_score || 0}`);

    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      node
        .attr('cx', (d: any) => d.x)
        .attr('cy', (d: any) => d.y);
        
      label
        .attr('x', (d: any) => d.x)
        .attr('y', (d: any) => d.y);
    });

    function dragstarted(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event: any, d: any) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }

    return () => {
      simulation.stop();
    };
  }, [graphData]);

  return (
    <div className="w-full h-full flex flex-col relative overflow-hidden">
      <svg ref={svgRef} className="flex-1 w-full" style={{ minHeight: '400px' }} />
      
      {/* Timeline Scrubber */}
      <div className="h-12 border-t border-white/5 bg-black/30 px-4 flex items-center gap-4 shrink-0 absolute bottom-0 left-0 right-0">
        <span className="text-xs font-mono text-slate-400">T-7D</span>
        <input 
          type="range" 
          min="0" 
          max="100" 
          defaultValue="100"
          className="flex-1 accent-red-500 h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer"
        />
        <span className="text-xs font-mono text-slate-400">NOW</span>
      </div>
    </div>
  );
}
