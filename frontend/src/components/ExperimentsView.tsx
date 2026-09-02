import React, { useState } from 'react';
import {
  FlaskConical,
  Play,
  RefreshCw,
  Layers,
  Sun
} from 'lucide-react';
import { runScalabilitySweep, runHeterogeneitySweep } from '../engine/benchmark';
import { ScalabilityResultPoint, HeterogeneityResultPoint } from '../types';

interface ExperimentsViewProps {}

export const ExperimentsView: React.FC<ExperimentsViewProps> = () => {
  const [activeExperiment, setActiveExperiment] = useState<'density' | 'shadow'>('density');
  const [scalabilityData, setScalabilityData] = useState<ScalabilityResultPoint[] | null>(null);
  const [heterogeneityData, setHeterogeneityData] = useState<HeterogeneityResultPoint[] | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [progress, setProgress] = useState<string>('');

  const handleRunDensitySweep = async () => {
    setLoading(true);
    setProgress('Running node density sweep across [30, 50, 80, 120, 160] nodes...');
    await new Promise(r => setTimeout(r, 20));
    try {
      const data = runScalabilitySweep([30, 50, 80, 120, 160], 200, 42);
      setScalabilityData(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
      setProgress('');
    }
  };

  const handleRunShadowSweep = async () => {
    setLoading(true);
    setProgress('Running shadow canopy occlusion sweep across [0.1, 0.3, 0.5, 0.7, 0.9]...');
    await new Promise(r => setTimeout(r, 20));
    try {
      const data = runHeterogeneitySweep([0.1, 0.3, 0.5, 0.7, 0.9], 50, 250, 42);
      setHeterogeneityData(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
      setProgress('');
    }
  };

  return (
    <div className="bg-[#090a0d] border border-[#1b1d26] rounded flex flex-col h-full overflow-hidden space-y-3 p-4">
      {/* Experiments Header Deck */}
      <div className="bg-[#050608] border border-[#1b1d26] p-3 rounded flex flex-wrap items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <FlaskConical className="w-4 h-4 text-slate-300" />
            <h2 className="text-xs font-semibold text-slate-200">
              Parametric Sensitivity & Scalability Experiments
            </h2>
          </div>
          <p className="text-[11px] text-slate-400 mt-1 max-w-xl">
            Execute batch parameter sweeps to evaluate algorithm performance scaling under varying node density and canopy shadow fractions.
          </p>
        </div>

        {/* Experiment Tab Selector */}
        <div className="flex items-center bg-[#07080a] p-0.5 rounded border border-[#1c1e28] text-xs font-medium">
          <button
            onClick={() => setActiveExperiment('density')}
            className={`px-2.5 py-1 rounded flex items-center gap-1.5 transition-colors ${
              activeExperiment === 'density'
                ? 'bg-[#181a24] text-slate-100 font-semibold border border-[#2a2e3e]'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>Density Scalability</span>
          </button>

          <button
            onClick={() => setActiveExperiment('shadow')}
            className={`px-2.5 py-1 rounded flex items-center gap-1.5 transition-colors ${
              activeExperiment === 'shadow'
                ? 'bg-[#181a24] text-slate-100 font-semibold border border-[#2a2e3e]'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Sun className="w-3.5 h-3.5" />
            <span>Shadow Occlusion</span>
          </button>
        </div>
      </div>

      {/* Density Sweep Section */}
      {activeExperiment === 'density' && (
        <div className="space-y-3">
          <div className="bg-[#050608] border border-[#1b1d26] p-3 rounded flex items-center justify-between">
            <div>
              <h3 className="text-xs font-semibold text-slate-200">
                Network Density Sweep (30 → 160 Sensor Nodes)
              </h3>
              <p className="text-[11px] text-slate-400 mt-0.5">
                Compares Baseline LEACH vs Proposed Time-DP + EH-LEACH across dense field deployments.
              </p>
            </div>
            <button
              onClick={handleRunDensitySweep}
              disabled={loading}
              className="py-1.5 px-3 rounded bg-[#181a24] hover:bg-[#202330] text-slate-200 border border-[#2a2e3e] text-xs font-medium flex items-center gap-1.5 transition-colors"
            >
              {loading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3 h-3 fill-current" />}
              <span>{loading ? 'Sweeping...' : 'Run Density Sweep'}</span>
            </button>
          </div>

          {loading && (
            <div className="p-2.5 bg-[#050608] border border-[#1b1d26] rounded text-center font-mono text-[11px] text-slate-300 animate-pulse">
              {progress}
            </div>
          )}

          {scalabilityData && !loading && (
            <div className="bg-[#050608] border border-[#1b1d26] rounded overflow-hidden p-3 space-y-2.5">
              <span className="text-xs font-semibold text-slate-200 block pb-2 border-b border-[#1b1d26]">
                Density Sweep Results
              </span>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-300 font-mono">
                  <thead className="bg-[#07080a] text-[10px] text-slate-400 uppercase border-b border-[#1b1d26]">
                    <tr>
                      <th className="p-2">Node Density</th>
                      <th className="p-2 text-right">Baseline FND</th>
                      <th className="p-2 text-right">Proposed FND</th>
                      <th className="p-2 text-right">FND Gain</th>
                      <th className="p-2 text-right">Baseline Alive</th>
                      <th className="p-2 text-right">Proposed Alive</th>
                      <th className="p-2 text-right">Compute</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#181a24] text-[10px]">
                    {scalabilityData.map((pt) => {
                      const fndBase = pt.baseline_fnd ?? 200;
                      const fndProp = pt.adaptive_fnd ?? 200;
                      const fndGain = fndProp - fndBase;

                      return (
                        <tr key={pt.nodes} className="hover:bg-[#101218]">
                          <td className="p-2 font-sans font-medium text-slate-200">{pt.nodes} Nodes</td>
                          <td className="p-2 text-right text-slate-400">Rd {pt.baseline_fnd ?? '>200'}</td>
                          <td className="p-2 text-right text-slate-200 font-bold">Rd {pt.adaptive_fnd ?? '>200'}</td>
                          <td className="p-2 text-right text-slate-300">
                            +{fndGain > 0 ? fndGain : 0} rds
                          </td>
                          <td className="p-2 text-right text-slate-400">{pt.baseline_alive}/{pt.nodes}</td>
                          <td className="p-2 text-right text-slate-200">{pt.adaptive_alive}/{pt.nodes}</td>
                          <td className="p-2 text-right text-slate-400">{pt.computation_ms.toFixed(0)} ms</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {activeExperiment === 'shadow' && (
        <div className="space-y-3">
          <div className="bg-[#050608] border border-[#1b1d26] p-3 rounded flex items-center justify-between">
            <div>
              <h3 className="text-xs font-semibold text-slate-200">
                Canopy Shadow Fraction Sweep (10% → 90% Occlusion)
              </h3>
              <p className="text-[11px] text-slate-400 mt-0.5">
                Simulates solar occlusion in heterogeneous terrain where shadowed nodes harvest 70% less energy.
              </p>
            </div>
            <button
              onClick={handleRunShadowSweep}
              disabled={loading}
              className="py-1.5 px-3 rounded bg-[#181a24] hover:bg-[#202330] text-slate-200 border border-[#2a2e3e] text-xs font-medium flex items-center gap-1.5 transition-colors"
            >
              {loading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3 h-3 fill-current" />}
              <span>{loading ? 'Sweeping...' : 'Run Shadow Sweep'}</span>
            </button>
          </div>

          {loading && (
            <div className="p-2.5 bg-[#050608] border border-[#1b1d26] rounded text-center font-mono text-[11px] text-slate-300 animate-pulse">
              {progress}
            </div>
          )}

          {heterogeneityData && !loading && (
            <div className="bg-[#050608] border border-[#1b1d26] rounded overflow-hidden p-3 space-y-2.5">
              <span className="text-xs font-semibold text-slate-200 block pb-2 border-b border-[#1b1d26]">
                Canopy Shadow Sweep Results
              </span>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-300 font-mono">
                  <thead className="bg-[#07080a] text-[10px] text-slate-400 uppercase border-b border-[#1b1d26]">
                    <tr>
                      <th className="p-2">Shadow Fraction</th>
                      <th className="p-2 text-right">Unaware FND</th>
                      <th className="p-2 text-right">Proposed FND</th>
                      <th className="p-2 text-right">Unaware Alive</th>
                      <th className="p-2 text-right">Proposed Alive</th>
                      <th className="p-2 text-right">Residual Energy</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#181a24] text-[10px]">
                    {heterogeneityData.map((pt) => (
                      <tr key={pt.shadowFraction} className="hover:bg-[#101218]">
                        <td className="p-2 font-sans font-medium text-slate-200">
                          {(pt.shadowFraction * 100).toFixed(0)}% Shade
                        </td>
                        <td className="p-2 text-right text-slate-400">Rd {pt.unaware_fnd ?? '>250'}</td>
                        <td className="p-2 text-right text-slate-200 font-bold">Rd {pt.adaptive_fnd ?? '>250'}</td>
                        <td className="p-2 text-right text-slate-400">{pt.unaware_alive} nodes</td>
                        <td className="p-2 text-right text-slate-200">{pt.adaptive_alive} nodes</td>
                        <td className="p-2 text-right text-slate-300">{pt.energyRetainedJ.toFixed(2)} J</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

