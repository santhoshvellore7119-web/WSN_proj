import React, { useState, useEffect } from 'react';
import { useSimulation } from '../hooks/useSimulation';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const BenchmarkView = () => {
  const { runBenchmark, loading, error, results } = useSimulation();
  const [benchmarkData, setBenchmarkData] = useState(null);
  const [parsingError, setParsingError] = useState(null);

  const handleReset = () => {
    setBenchmarkData(null);
    setParsingError(null);
  };

  const handleRunBenchmark = async () => {
    setParsingError(null);
    setBenchmarkData(null);
    try {
      await runBenchmark();
    } catch (err) {
      // Error is already set by the hook
    }
  };

  // Parse the benchmark results when they change
  // Note: results from the hook is the full response from the benchmark endpoint
  useEffect(() => {
    if (results && results.benchmark_output) {
      try {
        const parsed = parseBenchmarkOutput(results.benchmark_output);
        setBenchmarkData(parsed);
        setParsingError(null);
      } catch (err) {
        setParsingError(`Failed to parse benchmark results: ${err.message}`);
        setBenchmarkData(null);
      }
    } else if (results && !results.benchmark_output) {
      setParsingError('Benchmark results are not available in the expected format.');
      setBenchmarkData(null);
    }
  }, [results]);

  if (loading && !benchmarkData) {
    return (
      <div className="benchmark-view">
        <div className="benchmark-header">
          <h2>Network Benchmark</h2>
          <p>Run the standard 5-scenario benchmark to compare routing strategies</p>
        </div>
        <div className="benchmark-loading">
          <p>Running benchmark...</p>
        </div>
      </div>
    );
  }

  if (error && !benchmarkData) {
    return (
      <div className="benchmark-view">
        <div className="benchmark-header">
          <h2>Network Benchmark</h2>
          <p>Run the standard 5-scenario benchmark to compare routing strategies</p>
        </div>
        <div className="benchmark-error">
          <p>Error: {error}</p>
          <button onClick={handleReset}>Try Again</button>
        </div>
      </div>
    );
  }

  if (parsingError) {
    return (
      <div className="benchmark-view">
        <div className="benchmark-header">
          <h2>Network Benchmark</h2>
          <p>Run the standard 5-scenario benchmark to compare routing strategies</p>
        </div>
        <div className="benchmark-error">
          <p>{parsingError}</p>
          <button onClick={handleReset}>Try Again</button>
        </div>
      </div>
    );
  }

  if (!benchmarkData) {
    return (
      <div className="benchmark-view">
        <div className="benchmark-header">
          <h2>Network Benchmark</h2>
          <p>Run the standard 5-scenario benchmark to compare routing strategies</p>
        </div>
        <div className="benchmark-empty">
          <p>Click "Run Benchmark" to see comparative results of different routing strategies.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="benchmark-view">
      <div className="benchmark-header">
        <h2>Network Benchmark</h2>
        <p>Comparison of 9 standard configurations</p>
      </div>

      <div className="benchmark-controls">
        <button onClick={handleRunBenchmark}>
          {loading ? 'Running Benchmark...' : 'Run Benchmark'}
        </button>
        <button onClick={handleReset} style={{ marginLeft: '10px' }}>
          Reset
        </button>
      </div>

      {/* Results Table */}
      <div className="benchmark-table-container">
        <h3>Results Summary</h3>
        <table className="benchmark-table">
          <thead>
            <tr>
              <th>Configuration</th>
              <th>First Node Death (FND)</th>
              <th>Half Nodes Dead (HND)</th>
              <th>Alive Nodes (Final)</th>
              <th>Total Residual Energy (J)</th>
            </tr>
          </thead>
          <tbody>
            {benchmarkData.map((row, index) => (
              <tr key={index}>
                <td>{row.configuration}</td>
                <td>{row.fnd !== null ? row.fnd : 'N/A'}</td>
                <td>{row.hnd !== null ? row.hnd : 'N/A'}</td>
                <td>{row.alive_nodes}</td>
                <td>{row.total_energy.toFixed(4)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Charts */}
      <div className="benchmark-charts">
        <div className="chart-container">
          <h4>First Node Death (FND) by Configuration</h4>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={benchmarkData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="configuration" tick={false} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="fnd" name="FND" barSize={20} fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h4>Half Nodes Dead (HND) by Configuration</h4>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={benchmarkData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="configuration" tick={false} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="hnd" name="HND" barSize={20} fill="#82ca9d" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h4>Final Alive Nodes by Configuration</h4>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={benchmarkData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="configuration" tick={false} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="alive_nodes" name="Alive Nodes" barSize={20} fill="#ffc658" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h4>Total Residual Energy (J) by Configuration</h4>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={benchmarkData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="configuration" tick={false} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="total_energy" name="Total Energy" barSize={20} fill="#ff8042" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

// Function to parse the benchmark output text
function parseBenchmarkOutput(output) {
  // Find the table output in the text
  // The table is between the line "===" and the line "Finished!"
  const lines = output.split('\n');
  let tableStart = -1;
  let tableEnd = -1;

  for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes('=== Comprehensive Results Summary ===')) {
      tableStart = i + 2; // Skip the header line and the separator line
    }
    if (lines[i].includes('Finished! Benchmark results saved')) {
      tableEnd = i;
      break;
    }
  }

  if (tableStart === -1 || tableEnd === -1) {
    throw new Error('Could not locate the results table in the benchmark output.');
  }

  const tableLines = lines.slice(tableStart, tableEnd);
  const data = [];

  for (let i = 0; i < tableLines.length; i++) {
    const line = tableLines[i].trim();
    if (line.length === 0) continue;

    // Split by '|' and trim each cell
    const cells = line.split('|').map(cell => cell.trim());
    if (cells.length < 5) continue; // Skip if not enough columns

    const configuration = cells[0];
    const fndStr = cells[1];
    const hndStr = cells[2];
    const aliveStr = cells[3];
    const energyStr = cells[4];

    // Parse FND
    let fnd = null;
    if (fndStr !== 'N/A') {
      const fndNum = parseInt(fndStr, 10);
      if (!isNaN(fndNum)) {
        fnd = fndNum;
      }
    }

    // Parse HND
    let hnd = null;
    if (hndStr !== 'N/A') {
      const hndNum = parseInt(hndStr, 10);
      if (!isNaN(hndNum)) {
        hnd = hndNum;
      }
    }

    // Parse Alive Nodes (format: "x/y")
    let alive_nodes = 0;
    const aliveMatch = aliveStr.match(/^(\d+)\/\d+$/);
    if (aliveMatch) {
      alive_nodes = parseInt(aliveMatch[1], 10);
    } else {
      // Try to parse as a single number (if format is different)
      const aliveNum = parseInt(aliveStr, 10);
      if (!isNaN(aliveNum)) {
        alive_nodes = aliveNum;
      }
    }

    // Parse Total Energy
    let total_energy = 0;
    const energyNum = parseFloat(energyStr);
    if (!isNaN(energyNum)) {
      total_energy = energyNum;
    }

    data.push({
      configuration,
      fnd,
      hnd,
      alive_nodes,
      total_energy
    });
  }

  if (data.length === 0) {
    throw new Error('No data rows were parsed from the benchmark output.');
  }

  return data;
}

BenchmarkView.propTypes = {};

export default BenchmarkView;