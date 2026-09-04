import React, { useState } from 'react';
import {
  BarChart3,
  TrendingUp,
  FileJson,
  FileSpreadsheet
} from 'lucide-react';
import { SimulationResults, SimulationConfig } from '../types';
import { exportSimulationCSV } from '../utils/exportUtils';

interface AnalyticsChartsViewProps {
  results: SimulationResults | null;
  config: SimulationConfig;
}

export const AnalyticsChartsView: React.FC<AnalyticsChartsViewProps> = ({
  results,
  config
}) => {
  const [activeMetric, setActiveMetric] = useState<'lifetime' | 'energy' | 'fairness' | 'pdr'>('lifetime');

  if (!results) {
    return (
      <div className="bg-[#090a0d] border border-[#1b1d26] rounded p-8 flex flex-col items-center justify-center text-center h-full min-h-[400px]">
        <div className="w-10 h-10 rounded bg-[#101218] border border-[#20232e] flex items-center justify-center text-slate-400 mb-3">
          <BarChart3 className="w-5 h-5" />
        </div>
        <h3 className="text-xs font-semibold text-slate-200 mb-1">No Simulation Results to Analyze</h3>
        <p className="text-[11px] text-slate-400 max-w-sm">
          Run a simulation to generate comprehensive network lifetime, energy intake/drain, and QoS analytics.
        </p>
      </div>
    );
  }

  const { summary, time_series } = results;
  const numRounds = time_series.rounds.length;

  // Export JSON
  const handleExportJSON = () => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(results, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `wsn_sim_results_${Date.now()}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  // Export CSV using structured exporter
  const handleExportCSV = () => {
    if (results) {
      exportSimulationCSV(results);
    }
  };

  // Helper for responsive SVG line charts
  const renderSVGLineChart = (
    data: number[],
    color: string,
    minY: number = 0,
    maxY?: number,
    markers?: { round: number | null; label: string; color: string }[]
  ) => {
    const computedMaxY = maxY !== undefined ? maxY : Math.max(...data, 1);
    const width = 600;
    const height = 220;
    const padding = { top: 20, right: 30, bottom: 30, left: 50 };
    const chartW = width - padding.left - padding.right;
    const chartH = height - padding.top - padding.bottom;

    const points = data.map((val, idx) => {
      const x = padding.left + (idx / Math.max(1, data.length - 1)) * chartW;
      const normalizedY = (val - minY) / Math.max(1e-6, computedMaxY - minY);
      const y = padding.top + chartH - normalizedY * chartH;
      return `${x},${y}`;
    }).join(' ');

    return (
      <svg className="w-full h-auto" viewBox={`0 0 ${width} ${height}`}>
        <defs>
          <linearGradient id={`grad-${color}`} x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor={color} stopOpacity="0.15" />
            <stop offset="100%" stopColor={color} stopOpacity="0.0" />
          </linearGradient>
        </defs>

        {/* Grid lines */}
        {[0, 0.25, 0.5, 0.75, 1.0].map((t, idx) => {
          const yPos = padding.top + chartH - t * chartH;
          const labelVal = minY + t * (computedMaxY - minY);
          return (
            <g key={idx}>
              <line
                x1={padding.left}
                y1={yPos}
                x2={width - padding.right}
                y2={yPos}
                stroke="#171923"
                strokeWidth="1"
                strokeDasharray="2 2"
              />
              <text
                x={padding.left - 8}
                y={yPos + 3}
                fill="#64748b"
                fontSize="10"
                fontFamily="monospace"
                textAnchor="end"
              >
                {labelVal >= 1000 ? (labelVal / 1000).toFixed(1) + 'k' : labelVal.toFixed(1)}
              </text>
            </g>
          );
        })}

        {/* Fill area */}
        {points && (
          <polygon
            points={`${padding.left},${padding.top + chartH} ${points} ${width - padding.right},${padding.top + chartH}`}
            fill={`url(#grad-${color})`}
          />
        )}

        {/* Main Line */}
        <polyline
          fill="none"
          stroke={color}
          strokeWidth="1.8"
          strokeLinecap="round"
          strokeLinejoin="round"
          points={points}
        />

        {/* Specific Event Markers (FND, HND, LND) */}
        {markers && markers.map((m, idx) => {
          if (m.round === null || m.round < 0 || m.round >= data.length) return null;
          const markerX = padding.left + (m.round / Math.max(1, data.length - 1)) * chartW;
          return (
            <g key={`marker-${idx}`}>
              <line
                x1={markerX}
                y1={padding.top}
                x2={markerX}
                y2={padding.top + chartH}
                stroke={m.color}
                strokeWidth="1.2"
                strokeDasharray="3 2"
              />
              <circle
                cx={markerX}
                cy={padding.top + 8}
                r="3.5"
                fill={m.color}
              />
              <text
                x={markerX + 4}
                y={padding.top + 11}
                fill={m.color}
                fontSize="9"
                fontWeight="bold"
                fontFamily="monospace"
              >
                {m.label} (Rd {m.round})
              </text>
            </g>
          );
        })}

        {/* X-axis labels */}
        <text
          x={padding.left}
          y={height - 8}
          fill="#64748b"
          fontSize="10"
          fontFamily="monospace"
        >
          Rd 1
        </text>
        <text
          x={width / 2}
          y={height - 8}
          fill="#64748b"
          fontSize="10"
          fontFamily="monospace"
          textAnchor="middle"
        >
          Simulation Rounds
        </text>
        <text
          x={width - padding.right}
          y={height - 8}
          fill="#64748b"
          fontSize="10"
          fontFamily="monospace"
          textAnchor="end"
        >
          Rd {numRounds}
        </text>
      </svg>
    );
  };

  return (
    <div className="bg-[#090a0d] border border-[#1b1d26] rounded flex flex-col h-full overflow-hidden space-y-3 p-4">
      {/* Analytics KPI Header Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2">
        <div className="bg-[#050608] border border-[#1b1d26] p-2.5 rounded">
          <span className="text-[10px] text-slate-400 block font-medium">First Node Dead (FND)</span>
          <div className="flex items-baseline gap-1 mt-0.5">
            <span className="text-base font-bold font-mono text-slate-200">
              {summary.first_node_death_round ? `Rd ${summary.first_node_death_round}` : 'None'}
            </span>
          </div>
          <span className="text-[10px] text-slate-500 font-mono">stability threshold</span>
        </div>

        <div className="bg-[#050608] border border-[#1b1d26] p-2.5 rounded">
          <span className="text-[10px] text-slate-400 block font-medium">Half Nodes Dead (HND)</span>
          <div className="flex items-baseline gap-1 mt-0.5">
            <span className="text-base font-bold font-mono text-slate-200">
              {summary.half_nodes_dead_round ? `Rd ${summary.half_nodes_dead_round}` : 'None'}
            </span>
          </div>
          <span className="text-[10px] text-slate-500 font-mono">50% operational</span>
        </div>

        <div className="bg-[#050608] border border-[#1b1d26] p-2.5 rounded">
          <span className="text-[10px] text-slate-400 block font-medium">Final Alive Nodes</span>
          <div className="flex items-baseline gap-1 mt-0.5">
            <span className="text-base font-bold font-mono text-slate-200">
              {summary.final_alive_nodes}
            </span>
            <span className="text-[10px] font-mono text-slate-400">/ {summary.total_nodes}</span>
          </div>
          <span className="text-[10px] text-slate-500 font-mono">
            {summary.network_lifetime_efficiency.toFixed(1)}% survival
          </span>
        </div>

        <div className="bg-[#050608] border border-[#1b1d26] p-2.5 rounded">
          <span className="text-[10px] text-slate-400 block font-medium">Harvested Energy</span>
          <div className="flex items-baseline gap-1 mt-0.5">
            <span className="text-base font-bold font-mono text-slate-200">
              {(summary.total_harvested_energy * 1000).toFixed(1)}
            </span>
            <span className="text-[10px] font-mono text-slate-400">mJ</span>
          </div>
          <span className="text-[10px] text-slate-500 font-mono">ambient intake</span>
        </div>

        <div className="bg-[#050608] border border-[#1b1d26] p-2.5 rounded">
          <span className="text-[10px] text-slate-400 block font-medium">Consumed Energy</span>
          <div className="flex items-baseline gap-1 mt-0.5">
            <span className="text-base font-bold font-mono text-slate-200">
              {(summary.total_consumed_energy * 1000).toFixed(1)}
            </span>
            <span className="text-[10px] font-mono text-slate-400">mJ</span>
          </div>
          <span className="text-[10px] text-slate-500 font-mono">net expenditure</span>
        </div>

        <div className="bg-[#050608] border border-[#1b1d26] p-2.5 rounded">
          <span className="text-[10px] text-slate-400 block font-medium">DSU Detour Events</span>
          <div className="flex items-baseline gap-1 mt-0.5">
            <span className="text-base font-bold font-mono text-slate-200">
              {summary.total_reroutes}
            </span>
            <span className="text-[10px] font-mono text-slate-400">events</span>
          </div>
          <span className="text-[10px] text-slate-500 font-mono">reroutes</span>
        </div>

        <div className="bg-[#050608] border border-[#1b1d26] p-2.5 rounded">
          <span className="text-[10px] text-slate-400 block font-medium">Execution Time</span>
          <div className="flex items-baseline gap-1 mt-0.5">
            <span className="text-base font-bold font-mono text-slate-200">
              {summary.execution_time_ms.toFixed(0)}
            </span>
            <span className="text-[10px] font-mono text-slate-400">ms</span>
          </div>
          <span className="text-[10px] text-slate-500 font-mono">sim run time</span>
        </div>
      </div>

      {/* Main Chart Card */}
      <div className="bg-[#050608] border border-[#1b1d26] rounded p-3.5 space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-3 pb-2 border-b border-[#1b1d26]">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-slate-400" />
            <span className="text-xs font-semibold text-slate-200">
              Simulation Curves & Trends
            </span>
          </div>

          {/* Metric Selector Tabs */}
          <div className="flex items-center gap-2">
            <div className="flex items-center bg-[#07080a] p-0.5 rounded border border-[#1c1e28] text-xs">
              <button
                onClick={() => setActiveMetric('lifetime')}
                className={`px-2.5 py-1 rounded text-[11px] font-medium transition-colors ${
                  activeMetric === 'lifetime' ? 'bg-[#181a24] text-slate-100 font-semibold border border-[#2a2e3e]' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Lifetime
              </button>
              <button
                onClick={() => setActiveMetric('energy')}
                className={`px-2.5 py-1 rounded text-[11px] font-medium transition-colors ${
                  activeMetric === 'energy' ? 'bg-[#181a24] text-slate-100 font-semibold border border-[#2a2e3e]' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Residual Energy
              </button>
              <button
                onClick={() => setActiveMetric('fairness')}
                className={`px-2.5 py-1 rounded text-[11px] font-medium transition-colors ${
                  activeMetric === 'fairness' ? 'bg-[#181a24] text-slate-100 font-semibold border border-[#2a2e3e]' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Jain's Fairness
              </button>
              <button
                onClick={() => setActiveMetric('pdr')}
                className={`px-2.5 py-1 rounded text-[11px] font-medium transition-colors ${
                  activeMetric === 'pdr' ? 'bg-[#181a24] text-slate-100 font-semibold border border-[#2a2e3e]' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Delivery (PDR)
              </button>
            </div>

            {/* Export buttons */}
            <button
              onClick={handleExportCSV}
              className="p-1.5 rounded bg-[#101218] hover:bg-[#181a24] text-slate-300 border border-[#20232e] text-xs flex items-center gap-1 transition-colors"
              title="Export Time-Series as CSV"
            >
              <FileSpreadsheet className="w-3.5 h-3.5 text-slate-400" />
              <span className="hidden sm:inline text-[11px]">CSV</span>
            </button>

            <button
              onClick={handleExportJSON}
              className="p-1.5 rounded bg-[#101218] hover:bg-[#181a24] text-slate-300 border border-[#20232e] text-xs flex items-center gap-1 transition-colors"
              title="Export Full Results as JSON"
            >
              <FileJson className="w-3.5 h-3.5 text-slate-400" />
              <span className="hidden sm:inline text-[11px]">JSON</span>
            </button>
          </div>
        </div>

        {/* Selected Chart Rendering */}
        <div className="w-full">
          {activeMetric === 'lifetime' && (
            <div>
              <div className="flex justify-between text-xs text-slate-400 mb-2 font-mono">
                <span>Alive Nodes Progression over Time</span>
                <span className="text-slate-300">Total: {config.nodes} Sensors</span>
              </div>
              {renderSVGLineChart(
                time_series.alive_nodes,
                '#4b7260',
                0,
                config.nodes,
                [
                  { round: summary.first_node_death_round, label: 'FND', color: '#926323' },
                  { round: summary.half_nodes_dead_round, label: 'HND', color: '#8b3a3a' }
                ]
              )}
            </div>
          )}

          {activeMetric === 'energy' && (
            <div>
              <div className="flex justify-between text-xs text-slate-400 mb-2 font-mono">
                <span>Aggregate Network Residual Energy (Joules)</span>
                <span className="text-slate-300">Initial: {(config.nodes * config.init_energy).toFixed(2)} J</span>
              </div>
              {renderSVGLineChart(
                time_series.total_energy,
                '#526b88',
                0
              )}
            </div>
          )}

          {activeMetric === 'fairness' && (
            <div>
              <div className="flex justify-between text-xs text-slate-400 mb-2 font-mono">
                <span>Jain's Fairness Index</span>
                <span className="text-slate-300">Final: {summary.jains_fairness_final.toFixed(3)}</span>
              </div>
              {renderSVGLineChart(
                time_series.fairness_index,
                '#726a8a',
                0,
                1.0
              )}
            </div>
          )}

          {activeMetric === 'pdr' && (
            <div>
              <div className="flex justify-between text-xs text-slate-400 mb-2 font-mono">
                <span>Packet Delivery Ratio (PDR) per Round</span>
                <span className="text-slate-300">Avg: {(summary.average_pdr * 100).toFixed(1)}%</span>
              </div>
              {renderSVGLineChart(
                time_series.pdr_history,
                '#527488',
                0,
                1.0
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

