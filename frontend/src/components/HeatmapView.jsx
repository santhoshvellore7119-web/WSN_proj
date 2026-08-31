import React, { useState, useEffect, useRef } from 'react';
import * as d3 from 'd3';
import PropTypes from 'prop-types';

const HeatmapView = ({ simulationData }) => {
  const containerRef = useRef(null);
  const [currentRound, setCurrentRound] = useState(0);
  const [maxRounds, setMaxRounds] = useState(0);
  const [numNodes, setNumNodes] = useState(0);
  const [energyMatrix, setEnergyMatrix] = useState([]);

  // Update state when simulationData changes
  useEffect(() => {
    if (simulationData && simulationData.detailed_data) {
      const { energy_matrix } = simulationData.detailed_data;
      if (energy_matrix && energy_matrix.length > 0) {
        setEnergyMatrix(energy_matrix);
        setMaxRounds(energy_matrix.length);
        setNumNodes(energy_matrix[0].length);
        setCurrentRound(0); // reset to first round when new data comes
      }
    }
  }, [simulationData]);

  // Draw the heatmap using d3
  useEffect(() => {
    if (energyMatrix.length === 0 || numNodes === 0) return;

    const container = containerRef.current;
    if (!container) return;

    // Clear previous SVG
    d3.select(container).select('svg').remove();

    // Dimensions
    const margin = { top: 30, right: 20, bottom: 50, left: 60 };
    const width = container.clientWidth - margin.left - margin.right;
    const height = container.clientHeight - margin.top - margin.bottom - 80; // space for slider

    // Calculate cell size
    const cellSize = Math.min(
      width / maxRounds,
      height / numNodes
    );

    const svgWidth = maxRounds * cellSize + margin.left + margin.right;
    const svgHeight = numNodes * cellSize + margin.top + margin.bottom + 80;

    const svg = d3.select(container)
      .append('svg')
      .attr('width', svgWidth)
      .attr('height', svgHeight);

    // Create a group for the heatmap
    const heatmap = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Define color scale (energy to color)
    const maxEnergy = Math.max(...energyMatrix.flat());
    const colorScale = d3.scaleSequential()
      .domain([0, maxEnergy])
      .interpolator(d3.interpolateViridis);

    // Create x-axis (rounds)
    const xScale = d3.scaleLinear()
      .domain([0, maxRounds])
      .range([0, maxRounds * cellSize]);

    const xAxis = d3.axisBottom(xScale)
      .ticks(Math.min(maxRounds, 10))
      .tickFormat(d3.format('d'));

    heatmap.append('g')
      .attr('class', 'x-axis')
      .attr('transform', `translate(0, ${numNodes * cellSize})`)
      .call(xAxis);

    // Create y-axis (node IDs)
    const yScale = d3.scaleLinear()
      .domain([0, numNodes])
      .range([numNodes * cellSize, 0]); // inverted so node 0 is at top

    const yAxis = d3.axisLeft(yScale)
      .ticks(Math.min(numNodes, 10))
      .tickFormat(d3.format('d'));

    heatmap.append('g')
      .attr('class', 'y-axis')
      .call(yAxis);

    // Create tooltip
    const tooltip = d3.select(container)
      .append('div')
      .attr('class', 'heatmap-tooltip')
      .style('opacity', 0);

    // Draw cells
    const rows = heatmap.selectAll('.row')
      .data(energyMatrix)
      .enter()
      .append('g')
      .attr('class', 'row')
      .attr('transform', (d, i) => `translate(0, ${i * cellSize})`);

    rows.selectAll('.cell')
      .data((d, rowIndex) => d.map((energy, colIndex) => ({
        energy,
        rowIndex,
        colIndex
      })))
      .enter()
      .append('rect')
      .attr('class', 'cell')
      .attr('x', d => d.colIndex * cellSize)
      .attr('y', 0)
      .attr('width', cellSize)
      .attr('height', cellSize)
      .attr('fill', d => colorScale(d.energy))
      .on('mouseover', function(event, d) {
        tooltip.transition()
          .duration(200)
          .style('opacity', .9);
        tooltip.html(
          `Round: ${d.colIndex + 1}<br/>Node: ${d.rowIndex}<br/>Energy: ${d.energy.toFixed(4)} J`
          )
          .style('left', (event.pageX + 5) + 'px')
          .style('top', (event.pageY - 28) + 'px');
        })
      .on('mouseout', function() {
        tooltip.transition()
          .duration(500)
          .style('opacity', 0);
      });

    // Add axis labels
    heatmap.append('text')
      .attr('class', 'axis-label')
      .attr('text-anchor', 'middle')
      .attr('x', maxRounds * cellSize / 2)
      .attr('y', numNodes * cellSize + margin.bottom - 10)
      .text('Simulation Round');

    heatmap.append('text')
      .attr('class', 'axis-label')
      .attr('text-anchor', 'middle')
      .attr('transform', `rotate(-90)`)
      .attr('x', -numNodes * cellSize / 2)
      .attr('y', -margin.left + 15)
      .text('Node ID');

  }, [energyMatrix, numNodes, maxRounds, currentRound]);

  // If we want to highlight the current round column, we could add an overlay rectangle
  // But for simplicity, we'll just use the slider to change the view? Actually, we are not changing the heatmap view with the slider.
  // Let's adjust: we'll make the slider control the currentRound and then show a detailed view for that round below the heatmap.

  // We'll create a separate section below the heatmap to show the energy distribution for the selected round as a bar chart.

  // Reset currentRound when maxRounds changes (to avoid out of bounds)
  useEffect(() => {
    if (currentRound >= maxRounds) {
      setCurrentRound(maxRounds - 1);
    }
  }, [maxRounds, currentRound]);

  if (energyMatrix.length === 0) {
    return (
      <div className="heatmap-placeholder">
        <p>No simulation data available. Run a simulation to see the energy heatmap.</p>
      </div>
    );
  }

  // Get data for the selected round (for the bar chart below)
  const roundData = energyMatrix[currentRound] || [];

  return (
    <div className="heatmap-view">
      <div className="heatmap-header">
        <h2>Energy Heatmap (Time vs Node ID)</h2>
        <p>Color represents residual energy of each node at each round</p>
      </div>

      <div className="heatmap-container" ref={containerRef} />

      <div className="heatmap-slider-container">
        <label htmlFor="round-slider">Round: </label>
        <input
          type="range"
          id="round-slider"
          min="0"
          max={maxRounds - 1}
          value={currentRound}
          onChange={(e) => setCurrentRound(parseInt(e.target.value))}
          className="round-slider"
        />
        <span>{currentRound + 1} / {maxRounds}</span>
      </div>

      {/* Detailed view for selected round */}
      <div className="round-details">
        <h3>Energy Distribution at Round {currentRound + 1}</h3>
        {/* We'll use a simple bar chart using divs for now, or we can use recharts if we want */}
        <div className="bar-chart-container">
          {roundData.map((energy, nodeIndex) => (
            <div key={nodeIndex} className="bar-item">
              <label>Node {nodeIndex}</label>
              <div className="bar">
                <div
                  className="bar-fill"
                  style={{
                    width: `${Math.min(100, (energy / (Math.max(...energyMatrix.flat()) || 1)) * 100)}%`,
                    backgroundColor: d3.interpolateViridis(energy / (Math.max(...energyMatrix.flat()) || 1))
                  }}
                ></div>
              </div>
              <span className="bar-value">{energy.toFixed(4)} J</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

HeatmapView.propTypes = {
  simulationData: PropTypes.object
};

HeatmapView.defaultProps = {
  simulationData: {}
};

export default HeatmapView;