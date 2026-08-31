import React, { useState, useEffect, useRef } from 'react';
import PropTypes from 'prop-types';

const ScrubberView = ({ simulationData, networkData }) => {
  const [currentRound, setCurrentRound] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1); // rounds per second
  const playbackRef = useRef(null);

  const maxRounds = simulationData.time_series?.alive_nodes?.length || 0;

  // Handle play/pause functionality
  useEffect(() => {
    if (isPlaying && currentRound < maxRounds) {
      playbackRef.current = setTimeout(() => {
        setCurrentRound(prevRound => Math.min(prevRound + 1, maxRounds));
      }, 1000 / playbackSpeed);
    } else if (currentRound >= maxRounds) {
      setIsPlaying(false);
    }

    return () => {
      if (playbackRef.current) {
        clearTimeout(playbackRef.current);
      }
    };
  }, [isPlaying, currentRound, maxRounds, playbackSpeed]);

  // Reset when simulation data changes
  useEffect(() => {
    setCurrentRound(0);
    setIsPlaying(false);
  }, [simulationData]);

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleSpeedChange = (e) => {
    setPlaybackSpeed(parseInt(e.target.value));
  };

  const handleRoundChange = (e) => {
    setIsPlaying(false);
    setCurrentRound(parseInt(e.target.value));
  };

  // Get data for current round
  const getCurrentRoundData = () => {
    if (!simulationData.time_series || !simulationData.detailed_data) {
      return null;
    }

    const roundIndex = currentRound; // 0-indexed for arrays
    const roundNumber = currentRound + 1; // 1-indexed for display

    return {
      roundNumber,
      aliveNodes: simulationData.time_series.alive_nodes[roundIndex] || 0,
      totalEnergy: simulationData.time_series.total_energy[roundIndex] || 0,
      harvestedEnergy: simulationData.time_series.harvested_energy?.[roundIndex] || 0,
      clusterHeads: simulationData.detailed_data.cluster_heads_history?.[roundIndex] || [],
      energyMatrix: simulationData.detailed_data.energy_matrix?.[roundIndex] || [],
      nodePositions: simulationData.detailed_data.node_positions || {},
      baseStationPosition: simulationData.detailed_data.base_station_position || [50, 50]
    };
  };

  const currentData = getCurrentRoundData();

  if (!currentData) {
    return (
      <div className="scrubber-placeholder">
        <p>No simulation data available. Run a simulation to see process visualization.</p>
      </div>
    );
  }

  return (
    <div className="scrubber-view">
      <div className="scrubber-header">
        <h2>Process Visualization</h2>
        <p>Scrub through simulation rounds to see network evolution</p>
      </div>

      {/* Current Round Info */}
      <div className="round-info">
        <div className="round-stats">
          <div className="stat-item">
            <h4>Round</h4>
            <p>{currentData.roundNumber}</p>
          </div>
          <div className="stat-item">
            <h4>Alive Nodes</h4>
            <p>{currentData.aliveNodes}</p>
          </div>
          <div className="stat-item">
            <h4>Total Energy</h4>
            <p>{currentData.totalEnergy.toFixed(3)} J</p>
          </div>
          <div className="stat-item">
            <h4>Harvested Energy</h4>
            <p>{currentData.harvestedEnergy.toFixed(3)} J</p>
          </div>
        </div>
      </div>

      {/* Scrubber Controls */}
      <div className="scrubber-controls">
        <div className="playback-controls">
          <button
            onClick={handlePlayPause}
            disabled={maxRounds === 0}
            className={isPlaying ? 'pause-btn' : 'play-btn'}
          >
            {isPlaying ? '❚❚ Pause' : '▶️ Play'}
          </button>

          <label htmlFor="playback-speed">Speed: </label>
          <select id="playback-speed" value={playbackSpeed} onChange={handleSpeedChange}>
            <option value={0.5}>0.5x</option>
            <option value={1}>1x</option>
            <option value={2}>2x</option>
            <option value={5}>5x</option>
            <option value={10}>10x</option>
          </select>
          <span>x</span>
        </div>

        <div className="slider-container">
          <input
            type="range"
            min="0"
            max={maxRounds - 1}
            value={currentRound}
            onChange={handleRoundChange}
            className="round-slider"
          />
          <div className="slider-labels">
            <span>0</span>
            <span>{maxRounds}</span>
          </div>
        </div>
      </div>

      {/* Network Visualization (reuse NetworkView with current round data) */}
      <div className="network-visualization">
        <h3>Network State at Round {currentData.roundNumber}</h3>
        {/* We'll pass modified network data to NetworkView to show current round state */}
        {/* For now, we'll show a placeholder indicating this would integrate with NetworkView */}
        <div className="network-preview">
          <p>Network visualization showing:</p>
          <ul>
            <li>Node energies (color/size based on currentData.energyMatrix)</li>
            <li>Cluster heads: {currentData.clusterHeads.length} nodes highlighted</li>
            <li>Base station at ({currentData.baseStationPosition[0]}, {currentData.baseStationPosition[1]})</li>
            <li>{Object.keys(currentData.nodePositions).length} sensor nodes deployed</li>
          </ul>
          <div className="energy-bar-container">
            <p>Average Node Energy: {(currentData.energyMatrix.reduce((sum, val) => sum + val, 0) / currentData.energyMatrix.length || 0).toFixed(3)} J</p>
            <div className="energy-bar">
              <div
                className="energy-fill"
                style={{ width: `${Math.min(100, ((currentData.energyMatrix.reduce((sum, val) => sum + val, 0) / (currentData.energyMatrix.length || 1)) * 50))}%` }}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

ScrubberView.propTypes = {
  simulationData: PropTypes.object,
  networkData: PropTypes.object
};

ScrubberView.defaultProps = {
  simulationData: {},
  networkData: {}
};

export default ScrubberView;