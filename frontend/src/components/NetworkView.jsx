import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';

const NetworkView = ({ simulationData }) => {
  const containerRef = useRef(null);
  const [width, setWidth] = useState(800);
  const [height, setHeight] = useState(600);

  useEffect(() => {
    // Update dimensions when container size changes
    const updateDimensions = () => {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect();
        setWidth(Math.min(rect.width, 1000));
        setHeight(Math.min(rect.width * 0.75, 800));
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  useEffect(() => {
    if (!simulationData || !simulationData.detailed_data) return;

    const { detailed_data } = simulationData;
    const { node_positions, base_station_position } = detailed_data;
    const { cluster_heads_history, routes_history } = detailed_data;

    // Use the latest round data for cluster heads and routes
    const latestRound = cluster_heads_history.length - 1;
    const cluster_heads = cluster_heads_history[latestRound] || [];
    const latestRoutes = routes_history[latestRound] || {};

    // Create SVG container
    const svg = d3.select(containerRef.current)
      .selectAll('svg')
      .data([null])
      .join('svg')
      .attr('width', width)
      .attr('height', height)
      .attr('viewBox', `0 0 ${width} ${height}`)
      .attr('preserveAspectRatio', 'xMidYMid meet');

    // Clear previous elements
    svg.selectAll('*').remove();

    // Define scales for mapping coordinates to SVG
    const xScale = d3.scaleLinear()
      .domain([0, 100]) // Assuming area is 0-100, but we'll adjust based on actual data
      .range([50, width - 50]);

    const yScale = d3.scaleLinear()
      .domain([0, 100])
      .range([height - 50, 50]);

    // If we have actual position data, adjust scales
    if (Object.keys(node_positions).length > 0) {
      const xValues = Object.values(node_positions).map(p => p.x);
      const yValues = Object.values(node_positions).map(p => p.y);
      const xMin = Math.min(...xValues, base_station_position[0]);
      const xMax = Math.max(...xValues, base_station_position[0]);
      const yMin = Math.min(...yValues, base_station_position[1]);
      const yMax = Math.max(...yValues, base_station_position[1]);

      // Add padding
      const padding = 10;

      xScale.domain([xMin - padding, xMax + padding]).range([50, width - 50]);
      yScale.domain([yMax + padding, yMin - padding]).range([50, height - 50]); // Inverted for SVG
    }

    // Draw connections (routes) first (so they appear behind nodes)
    const connections = svg.append('g').attr('class', 'connections');

    Object.entries(latestRoutes).forEach(([chId, routeInfo]) => {
      const [path] = routeInfo || [];
      if (path && path.length >= 2) {
        const pathCoords = path.map(nodeId => {
          if (nodeId === -1) { // Base station
            return [base_station_position[0], base_station_position[1]];
          }
          const pos = node_positions[nodeId];
          return pos ? [pos.x, pos.y] : [0, 0];
        }).filter(coord => coord[0] !== 0 || coord[1] !== 0); // Filter out invalid positions

        if (pathCoords.length >= 2) {
          const line = d3.line()
            .x(d => xScale(d[0]))
            .y(d => yScale(d[1]))
            .curve(d3.curveLinear);

          connections.append('path')
            .datum(pathCoords)
            .attr('fill', 'none')
            .attr('stroke', '#28a745')
            .attr('stroke-width', 2)
            .attr('stroke-dasharray', '5,5')
            .attr('d', line);
        }
      }
    });

    // Draw base station
    const baseStationGroup = svg.append('g').attr('class', 'base-station');
    const baseStationX = xScale(base_station_position[0]);
    const baseStationY = yScale(base_station_position[1]);

    baseStationGroup.append('circle')
      .attr('cx', baseStationX)
      .attr('cy', baseStationY)
      .attr('r', 18)
      .attr('fill', '#ffc107')
      .attr('stroke', '#000')
      .attr('stroke-width', 2);

    baseStationGroup.append('text')
      .attr('x', baseStationX)
      .attr('y', baseStationY - 25)
      .attr('text-anchor', 'middle')
      .attr('font-size', '14px')
      .attr('font-weight', 'bold')
      .text('Base Station');

    // Draw nodes
    const nodesGroup = svg.append('g').attr('class', 'nodes');

    Object.entries(node_positions).forEach(([nodeIdStr, pos]) => {
      const nodeId = parseInt(nodeIdStr);
      const isClusterHead = cluster_heads.includes(nodeId);
      const nodeX = xScale(pos.x);
      const nodeY = yScale(pos.y);

      // Node circle
      nodesGroup.append('circle')
        .attr('cx', nodeX)
        .attr('cy', nodeY)
        .attr('r', isClusterHead ? 12 : 8)
        .attr('fill', isClusterHead ? '#dc3545' : '#007bff')
        .attr('stroke', '#000')
        .attr('stroke-width', 1.5);

      // Node ID label
      nodesGroup.append('text')
        .attr('x', nodeX)
        .attr('y', nodeY + 20)
        .attr('text-anchor', 'middle')
        .attr('font-size', '10px')
        .attr('font-weight', 'bold')
        .text(nodeId);
    });

    // Add legend
    const legend = svg.append('g').attr('class', 'legend').attr('transform', `translate(${width - 150}, 20)`);

    legend.append('circle').attr('cx', 0).attr('cy', 0).attr('r', 8).attr('fill', '#007bff');
    legend.append('text').attr('x', 15).attr('y', 4).attr('font-size', '12px').text('Member Node');

    legend.append('circle').attr('cx', 0).attr('cy', 20).attr('r', 12).attr('fill', '#dc3545');
    legend.append('text').attr('x', 15).attr('y', 24).attr('font-size', '12px').text('Cluster Head');

    legend.append('circle').attr('cx', 0).attr('cy', 40).attr('r', 18).attr('fill', '#ffc107');
    legend.append('text').attr('x', 15).attr('y', 44).attr('font-size', '12px').text('Base Station');

    legend.append('path').attr('d', 'M-5,60 L15,60').attr('stroke', '#28a745').attr('stroke-width', 2).attr('stroke-dasharray', '5,5');
    legend.append('text').attr('x', 20).attr('y', 64).attr('font-size', '12px').text('Route to BS');
  }, [simulationData, width, height]);

  return (
    <div className="network-view-container" ref={containerRef}>
      <h2>Network Topology</h2>
      <div className="network-visualization">
        {/* SVG will be injected here by D3 */}
      </div>
      {!simulationData && (
        <div className="placeholder">
          Run a simulation to see the network topology
        </div>
      )}
    </div>
  );
};

export default NetworkView;