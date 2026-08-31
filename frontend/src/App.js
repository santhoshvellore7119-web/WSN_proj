import React, { useState } from 'react';
import { getDefaultConfig } from './utils/constants';
import ControlPanel from './components/ControlPanel';
import NetworkView from './components/NetworkView';
import Chart from './components/Chart';
import { useSimulation } from './hooks/useSimulation';
import './App.css';

function App() {
  const [config, setConfig] = useState(getDefaultConfig());
  const {
    runSimulation,
    runBenchmark,
    loading,
    error,
    results,
    jobId,
    reset
  } = useSimulation();

  const [activeTab, setActiveTab] = useState('results'); // results, network, charts

  const handleRunSimulation = () => {
    runSimulation(config);
    setActiveTab('results');
  };

  const handleRunBenchmark = () => {
    runBenchmark(config);
    setActiveTab('results');
  };

  // Process results for visualization
  const processedResults = results?.results || {};

  return (
    <div className="App">
      <header className="App-header">
        <h1>WSN Energy-Harvesting Routing Simulator</h1>
        <p>A deployment planning tool for energy-harvesting wireless sensor networks</p>
      </header>

      <div className="main-content">
        {/* Control Panel */}
        <aside className="control-panel-sidebar">
          <ControlPanel
            onRunSimulation={handleRunSimulation}
            config={config}
            setConfig={setConfig}
            loading={loading}
            error={error}
          />

          {/* Benchmark Button */}
          <button
            onClick={handleRunBenchmark}
            disabled={loading}
            className="benchmark-button"
          >
            {loading ? 'Running Benchmark...' : 'Run Benchmark'}
          </button>
        </aside>

        {/* Main Content Area */}
        <main className="main-content-area">
          {/* Results Tab */}
          {activeTab === 'results' && (
            <div className="tab-content">
              {loading && !results && (
                <div className="loading-indicator">
                  Running simulation... Please wait.
                </div>
              )}

              {error && (
                <div className="error-message">
                  <strong>Error:</strong> {error}
                </div>
              )}

              {results && results.status === 'completed' && (
                <div className="results-summary">
                  <h2>Simulation Results</h2>
                  <div className="results-grid">
                    <div className="result-card">
                      <h3>Completed Rounds</h3>
                      <p className="result-value">
                        {processedResults.summary?.completed_rounds || 'N/A'}
                      </p>
                    </div>
                    <div className="result-card">
                      <h3>First Node Death (FND)</h3>
                      <p className="result-value">
                        {processedResults.summary?.first_node_death_round || 'None'}
                      </p>
                    </div>
                    <div className="result-card">
                      <h3>Half Nodes Dead (HND)</h3>
                      <p className="result-value">
                        {processedResults.summary?.half_nodes_dead_round || 'None'}
                      </p>
                    </div>
                    <div className="result-card">
                      <h3>Final Alive Nodes</h3>
                      <p className="result-value">
                        {processedResults.summary?.final_alive_nodes || '0'} /
                        {processedResults.summary?.total_nodes || config.nodes}
                      </p>
                    </div>
                    <div className="result-card">
                      <h3>Final Total Energy</h3>
                      <p className="result-value">
                        {processedResults.summary?.final_total_energy?.toFixed(4) || '0.0000'} J
                      </p>
                    </div>
                  </div>

                  {jobId && (
                    <div className="job-info">
                      Job ID: {jobId}
                    </div>
                  )}
                </div>
              )}

              {results && results.status === 'pending' && (
                <div className="job-pending">
                  Simulation is running... Check back in a few moments.
                </div>
              )}

              {results && results.status === 'failed' && (
                <div className="job-failed">
                  Simulation failed: {results.error}
                </div>
              )}
            </div>
          )}

          {/* Network Tab */}
          {activeTab === 'network' && (
            <div className="tab-content">
              <NetworkView simulationData={processedResults} />
            </div>
          )}

          {/* Charts Tab */}
          {activeTab === 'charts' && (
            <div className="tab-content">
              {processedResults.time_series ? (
                <>
                  <Chart
                    data={processedResults.time_series.alive_nodes.map((val, i) => ({
                      round: i + 1,
                      alive_nodes: val
                    }))}
                    xKey="round"
                    yKeys={["alive_nodes"]}
                    title="Alive Nodes Over Time"
                    unit="nodes"
                  />

                  <Chart
                    data={processedResults.time_series.total_energy.map((val, i) => ({
                      round: i + 1,
                      total_energy: val
                    }))}
                    xKey="round"
                    yKeys={["total_energy"]}
                    title="Total Residual Energy Over Time"
                    unit="Joules"
                  />

                  {processedResults.time_series.harvested_energy && processedResults.time_series.harvested_energy.length > 0 && (
                    <Chart
                      data={processedResults.time_series.harvested_energy.map((val, i) => ({
                        round: i + 1,
                        harvested_energy: val
                      }))}
                      xKey="round"
                      yKeys={["harvested_energy"]}
                      title="Total Harvested Energy Over Time"
                      unit="Joules"
                    />
                  )}
                </>
              ) : (
                <div className="chart-placeholder">
                  No time-series data available
                </div>
              )}
            </div>
          )}
        </main>
      </div>

      {/* Tab Navigation */}
      <div className="tab-navigation">
        <button
          className={activeTab === 'results' ? 'active' : ''}
          onClick={() => setActiveTab('results')}
          disabled={loading && !results}
        >
          Results
        </button>
        <button
          className={activeTab === 'network' ? 'active' : ''}
          onClick={() => setActiveTab('network')}
          disabled={loading && !results}
        >
          Network View
        </button>
        <button
          className={activeTab === 'charts' ? 'active' : ''}
          onClick={() => setActiveTab('charts')}
          disabled={loading && !results}
        >
          Charts
        </button>
      </div>
    </div>
  );
}

export default App;