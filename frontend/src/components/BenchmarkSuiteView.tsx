import React from 'react';
import {
  Activity,
  Play,
  Award,
  RefreshCw
} from 'lucide-react';
import { BenchmarkResults } from '../types';

interface BenchmarkSuiteViewProps {
  benchmarkResults: BenchmarkResults | null;
  loading: boolean;
  onRunBenchmark: () => void;
  progressText: string;
}

export const BenchmarkSuiteView: React.FC<BenchmarkSuiteViewProps> = ({
  benchmarkResults,
  loading,
  onRunBenchmark,
  progressText
}) => {
  return (
    <div className="bg-[#090a0d] border border-[#1b1d26] rounded flex flex-col h-full overflow-hidden space-y-3 p-4">
      {/* Benchmark Header Deck */}
      <div className="bg-[#050608] border border-[#1b1d26] p-3 rounded flex flex-wrap items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <Award className="w-4 h-4 text-slate-300" />
            <h2 className="text-xs font-semibold text-slate-200">
              9-Scenario Comparative Benchmark Suite
            </h2>
          </div>
          <p className="text-[11px] text-slate-400 mt-1 max-w-xl">
            Evaluate standard baseline LEACH vs Multi-hop Dijkstra vs Proposed EH-LEACH with Time-Augmented DP and DSU live reroutes across solar, canopy shade, and Poisson regimes.
          </p>
        </div>

        <button
          onClick={onRunBenchmark}
          disabled={loading}
          className={`py-1.5 px-3.5 rounded font-medium text-xs flex items-center gap-1.5 transition-all border ${
            loading
              ? 'bg-[#101218] text-slate-500 cursor-not-allowed border-[#1f2230]'
              : 'bg-[#181a24] hover:bg-[#202330] text-slate-200 border-[#2a2e3e]'
          }`}
        >
          {loading ? (
            <>
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              <span>Running Suite (9 Scenarios)...</span>
            </>
          ) : (
            <>
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>Execute Benchmark Suite</span>
            </>
          )}
        </button>
      </div>

      {loading && progressText && (
        <div className="bg-[#050608] border border-[#1b1d26] p-2.5 rounded text-center font-mono text-[11px] text-slate-300 animate-pulse">
          {progressText}
        </div>
      )}

      {/* Benchmark Results Tables and Visuals */}
      {!benchmarkResults && !loading && (
        <div className="bg-[#050608] border border-[#1b1d26] rounded p-8 flex flex-col items-center justify-center text-center">
          <div className="w-10 h-10 rounded bg-[#101218] border border-[#20232e] flex items-center justify-center text-slate-400 mb-3">
            <Activity className="w-5 h-5" />
          </div>
          <h3 className="text-xs font-semibold text-slate-200 mb-1">
            Benchmark Suite Not Yet Executed
          </h3>
          <p className="text-[11px] text-slate-400 max-w-md mb-3">
            Click "Execute Benchmark Suite" to run 9 distinct WSN configurations simultaneously and compare First Node Dead (FND), residual energy, and rerouting performance.
          </p>
          <button
            onClick={onRunBenchmark}
            className="py-1.5 px-3 rounded bg-[#181a24] hover:bg-[#202330] text-slate-200 border border-[#2a2e3e] text-xs font-medium flex items-center gap-1.5 transition-colors"
          >
            <Play className="w-3 h-3 fill-current" />
            <span>Run Benchmark Now</span>
          </button>
        </div>
      )}

      {benchmarkResults && (
        <div className="space-y-3">
          {/* Comparative Bar Visualization for FND and Alive Nodes */}
          <div className="bg-[#050608] border border-[#1b1d26] rounded p-3 space-y-2.5">
            <div className="flex items-center justify-between pb-2 border-b border-[#1b1d26]">
              <span className="text-xs font-semibold text-slate-200">
                Network Lifetime Comparison (First Node Dead & Node Survival)
              </span>
              <span className="text-[10px] font-mono text-slate-400">
                {benchmarkResults.nodesCount} Nodes • {benchmarkResults.maxRounds} Rounds
              </span>
            </div>

            <div className="space-y-2">
              {benchmarkResults.scenarios.map((sc) => {
                const maxRounds = benchmarkResults.maxRounds;
                const fndVal = sc.fnd ?? maxRounds;
                const fndPercent = (fndVal / maxRounds) * 100;
                const alivePercent = (sc.finalAliveNodes / sc.totalNodes) * 100;

                const isProposed = sc.strategy === 'Adaptive (Time-DP + DSU)';

                return (
                  <div
                    key={sc.id}
                    className={`p-2 rounded border text-xs space-y-1.5 transition-all ${
                      isProposed
                        ? 'bg-[#10131c] border-[#252c3e]'
                        : 'bg-[#07080a] border-[#181a22]'
                    }`}
                  >
                    <div className="flex flex-wrap items-center justify-between gap-1">
                      <div className="flex items-center gap-2">
                        <span className={`w-1.5 h-1.5 rounded-full ${
                          isProposed ? 'bg-slate-300' : 'bg-slate-500'
                        }`} />
                        <span className="font-medium text-slate-200">{sc.name}</span>
                        <span className="text-[9px] font-mono px-1 py-0.2 rounded bg-[#101218] text-slate-400 border border-[#20232e]">
                          {sc.category}
                        </span>
                      </div>

                      <div className="flex items-center gap-3 font-mono text-[10px]">
                        <span className="text-slate-300">
                          FND: {sc.fnd ? `Rd ${sc.fnd}` : `> Rd ${maxRounds}`}
                        </span>
                        <span className="text-slate-400">
                          Alive: {sc.finalAliveNodes}/{sc.totalNodes} ({alivePercent.toFixed(0)}%)
                        </span>
                      </div>
                    </div>

                    {/* Progress Bar of Lifetime */}
                    <div className="w-full bg-[#101218] h-1.5 rounded overflow-hidden flex">
                      <div
                        className={`h-full ${
                          isProposed ? 'bg-[#4a5f78]' : 'bg-[#2a3242]'
                        }`}
                        style={{ width: `${Math.min(100, fndPercent)}%` }}
                        title={`First Node Dead: Round ${fndVal}`}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Detailed Benchmark Summary Matrix */}
          <div className="bg-[#050608] border border-[#1b1d26] rounded overflow-hidden">
            <div className="p-2.5 border-b border-[#1b1d26] flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-200">
                Evaluation Results Matrix
              </span>
              <span className="text-[10px] font-mono text-slate-400">
                {benchmarkResults.timestamp}
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-[#07080a] text-[10px] uppercase font-mono text-slate-400 border-b border-[#1b1d26]">
                  <tr>
                    <th className="p-2.5">Scenario Name</th>
                    <th className="p-2.5">Category</th>
                    <th className="p-2.5">Strategy</th>
                    <th className="p-2.5 text-right">FND (Rds)</th>
                    <th className="p-2.5 text-right">HND (Rds)</th>
                    <th className="p-2.5 text-right">Alive Nodes</th>
                    <th className="p-2.5 text-right">Harvested (mJ)</th>
                    <th className="p-2.5 text-right">Residual (J)</th>
                    <th className="p-2.5 text-right">Reroutes</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#181a24] font-mono text-[10px]">
                  {benchmarkResults.scenarios.map((sc) => {
                    const isProposed = sc.strategy === 'Adaptive (Time-DP + DSU)';
                    return (
                      <tr
                        key={sc.id}
                        className={`hover:bg-[#101218] transition-colors ${
                          isProposed ? 'bg-[#0f121a] text-slate-200' : ''
                        }`}
                      >
                        <td className="p-2.5 font-sans font-medium text-slate-200 flex items-center gap-1.5">
                          {isProposed && <Award className="w-3 h-3 text-slate-400 inline" />}
                          {sc.name}
                        </td>
                        <td className="p-2.5 text-slate-400 font-sans">{sc.category}</td>
                        <td className="p-2.5 font-sans">
                          <span className={`px-1.5 py-0.5 rounded text-[9px] ${
                            isProposed ? 'bg-[#181a24] text-slate-200 border border-[#2a2e3e]' : 'bg-[#101218] text-slate-400 border border-[#1f2230]'
                          }`}>
                            {sc.strategy}
                          </span>
                        </td>
                        <td className="p-2.5 text-right text-slate-300">
                          {sc.fnd ?? `>${benchmarkResults.maxRounds}`}
                        </td>
                        <td className="p-2.5 text-right text-slate-400">
                          {sc.hnd ?? `>${benchmarkResults.maxRounds}`}
                        </td>
                        <td className="p-2.5 text-right text-slate-200">
                          {sc.finalAliveNodes} / {sc.totalNodes}
                        </td>
                        <td className="p-2.5 text-right text-slate-300">
                          {(sc.totalHarvested * 1000).toFixed(1)}
                        </td>
                        <td className="p-2.5 text-right text-slate-300">
                          {sc.finalTotalEnergy.toFixed(2)}
                        </td>
                        <td className="p-2.5 text-right text-slate-400">
                          {sc.rerouteCount}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

