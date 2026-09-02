import React, { useState } from 'react';
import {
  Play,
  Settings2,
  Sun,
  Radio,
  Cpu,
  RefreshCw,
  Sliders,
  ChevronDown,
  ChevronUp,
  Flame,
  ShieldCheck
} from 'lucide-react';
import { SimulationConfig, HarvestingProfileType, RoutingAlgorithmType, TopologyDistribution } from '../types';

interface ControlPanelProps {
  config: SimulationConfig;
  onChangeConfig: (newConfig: SimulationConfig) => void;
  onRunSimulation: () => void;
  loading: boolean;
  progressText: string;
}

export const ControlPanel: React.FC<ControlPanelProps> = ({
  config,
  onChangeConfig,
  onRunSimulation,
  loading,
  progressText
}) => {
  const [activeSection, setActiveSection] = useState<'topology' | 'harvesting' | 'routing' | 'advanced'>('topology');
  const [collapsed, setCollapsed] = useState<boolean>(false);

  const updateField = <K extends keyof SimulationConfig>(key: K, value: SimulationConfig[K]) => {
    onChangeConfig({
      ...config,
      [key]: value
    });
  };

  const randomizeSeed = () => {
    updateField('seed', Math.floor(Math.random() * 10000) + 1);
  };

  return (
    <aside className="bg-[#090a0d] border border-[#1b1d26] rounded flex flex-col overflow-hidden h-full">
      {/* Panel Header */}
      <div className="p-3 bg-[#050608] border-b border-[#1b1d26] flex items-center justify-between">
        <div className="flex items-center gap-2 text-slate-300 text-xs font-semibold">
          <Settings2 className="w-4 h-4 text-slate-400" />
          <span>Simulation Parameters</span>
        </div>
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="text-slate-400 hover:text-slate-200 p-1 rounded hover:bg-[#14161f] transition-colors"
          title={collapsed ? 'Expand panel' : 'Collapse panel'}
        >
          {collapsed ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
        </button>
      </div>

      {!collapsed && (
        <>
          {/* Section Tabs */}
          <div className="flex border-b border-[#1b1d26] bg-[#050608] p-1 text-xs font-medium gap-1">
            <button
              onClick={() => setActiveSection('topology')}
              className={`flex-1 py-1.5 px-2 rounded flex items-center justify-center gap-1.5 transition-colors ${
                activeSection === 'topology'
                  ? 'bg-[#181a24] text-slate-100 font-semibold border border-[#2b3042]'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-[#0e1016]'
              }`}
            >
              <Radio className="w-3 h-3" />
              <span>Network</span>
            </button>
            <button
              onClick={() => setActiveSection('harvesting')}
              className={`flex-1 py-1.5 px-2 rounded flex items-center justify-center gap-1.5 transition-colors ${
                activeSection === 'harvesting'
                  ? 'bg-[#181a24] text-slate-100 font-semibold border border-[#2b3042]'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-[#0e1016]'
              }`}
            >
              <Sun className="w-3 h-3" />
              <span>Harvesting</span>
            </button>
            <button
              onClick={() => setActiveSection('routing')}
              className={`flex-1 py-1.5 px-2 rounded flex items-center justify-center gap-1.5 transition-colors ${
                activeSection === 'routing'
                  ? 'bg-[#181a24] text-slate-100 font-semibold border border-[#2b3042]'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-[#0e1016]'
              }`}
            >
              <Cpu className="w-3 h-3" />
              <span>Routing</span>
            </button>
            <button
              onClick={() => setActiveSection('advanced')}
              className={`flex-1 py-1.5 px-2 rounded flex items-center justify-center gap-1.5 transition-colors ${
                activeSection === 'advanced'
                  ? 'bg-[#181a24] text-slate-100 font-semibold border border-[#2b3042]'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-[#0e1016]'
              }`}
            >
              <Sliders className="w-3 h-3" />
              <span>Physics</span>
            </button>
          </div>

          {/* Parameters Body */}
          <div className="p-3.5 space-y-3.5 overflow-y-auto max-h-[calc(100vh-280px)] text-xs text-slate-300">
            {/* 1. Network Topology Section */}
            {activeSection === 'topology' && (
              <div className="space-y-3">
                <div className="grid grid-cols-2 gap-2.5">
                  <div>
                    <label className="block text-[11px] font-medium text-slate-400 mb-1">
                      Sensor Nodes ({config.nodes})
                    </label>
                    <input
                      id="input-nodes-count"
                      type="number"
                      min={10}
                      max={300}
                      step={10}
                      value={config.nodes}
                      onChange={(e) => updateField('nodes', Math.max(10, parseInt(e.target.value) || 50))}
                      className="w-full bg-[#050608] border border-[#1e212c] rounded px-2.5 py-1.5 font-mono text-slate-200 focus:border-slate-500 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-[11px] font-medium text-slate-400 mb-1">
                      Rounds ({config.rounds})
                    </label>
                    <input
                      id="input-rounds-count"
                      type="number"
                      min={50}
                      max={1000}
                      step={50}
                      value={config.rounds}
                      onChange={(e) => updateField('rounds', Math.max(10, parseInt(e.target.value) || 200))}
                      className="w-full bg-[#050608] border border-[#1e212c] rounded px-2.5 py-1.5 font-mono text-slate-200 focus:border-slate-500 focus:outline-none"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2.5">
                  <div>
                    <label className="block text-[11px] font-medium text-slate-400 mb-1">
                      Area Width/Height (m)
                    </label>
                    <input
                      id="input-area-size"
                      type="number"
                      min={30}
                      max={500}
                      step={10}
                      value={config.area}
                      onChange={(e) => {
                        const val = Math.max(30, parseFloat(e.target.value) || 100);
                        onChangeConfig({
                          ...config,
                          area: val,
                          bs_x: Math.round(val / 2),
                          bs_y: Math.round(val / 2)
                        });
                      }}
                      className="w-full bg-[#050608] border border-[#1e212c] rounded px-2.5 py-1.5 font-mono text-slate-200 focus:border-slate-500 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-[11px] font-medium text-slate-400 mb-1">
                      Cluster Ratio (CH %)
                    </label>
                    <div className="flex items-center gap-2">
                      <input
                        id="input-cluster-ratio"
                        type="range"
                        min={0.02}
                        max={0.20}
                        step={0.01}
                        value={config.cluster_ratio}
                        onChange={(e) => updateField('cluster_ratio', parseFloat(e.target.value))}
                        className="flex-1 accent-slate-400 cursor-pointer"
                      />
                      <span className="font-mono text-[11px] text-slate-300 w-8 text-right">
                        {(config.cluster_ratio * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2.5">
                  <div>
                    <label className="block text-[11px] font-medium text-slate-400 mb-1">
                      Init Battery (Joules)
                    </label>
                    <input
                      id="input-init-energy"
                      type="number"
                      min={0.01}
                      max={10.0}
                      step={0.05}
                      value={config.init_energy}
                      onChange={(e) => updateField('init_energy', Math.max(0.01, parseFloat(e.target.value) || 0.15))}
                      className="w-full bg-[#050608] border border-[#1e212c] rounded px-2.5 py-1.5 font-mono text-slate-200 focus:border-slate-500 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-[11px] font-medium text-slate-400 mb-1">
                      Max Battery Cap (J)
                    </label>
                    <input
                      id="input-max-capacity"
                      type="number"
                      min={0.05}
                      max={20.0}
                      step={0.1}
                      value={config.max_capacity}
                      onChange={(e) => updateField('max_capacity', Math.max(config.init_energy, parseFloat(e.target.value) || 1.0))}
                      className="w-full bg-[#050608] border border-[#1e212c] rounded px-2.5 py-1.5 font-mono text-slate-200 focus:border-slate-500 focus:outline-none"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-[11px] font-medium text-slate-400 mb-1">
                    Spatial Node Distribution
                  </label>
                  <select
                    id="select-node-distribution"
                    value={config.topology_distribution || 'uniform'}
                    onChange={(e) => updateField('topology_distribution', e.target.value as TopologyDistribution)}
                    className="w-full bg-[#050608] border border-[#1e212c] rounded px-2.5 py-1.5 text-slate-200 focus:border-slate-500 focus:outline-none cursor-pointer"
                  >
                    <option value="uniform">Uniform Random Placement</option>
                    <option value="poisson_cluster">Poisson Clustered Deployment</option>
                    <option value="grid">Grid Topology with Jitter</option>
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-2.5">
                  <div>
                    <label className="block text-[11px] font-medium text-slate-400 mb-1">
                      Base Station (X, Y)
                    </label>
                    <div className="flex items-center gap-1.5">
                      <input
                        type="number"
                        value={config.bs_x}
                        onChange={(e) => updateField('bs_x', parseFloat(e.target.value) || 0)}
                        className="w-1/2 bg-[#050608] border border-[#1e212c] rounded px-2 py-1 font-mono text-[11px] text-slate-200"
                        title="Base Station X position"
                      />
                      <input
                        type="number"
                        value={config.bs_y}
                        onChange={(e) => updateField('bs_y', parseFloat(e.target.value) || 0)}
                        className="w-1/2 bg-[#050608] border border-[#1e212c] rounded px-2 py-1 font-mono text-[11px] text-slate-200"
                        title="Base Station Y position"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-[11px] font-medium text-slate-400 mb-1">
                      Random Seed
                    </label>
                    <div className="flex items-center gap-1.5">
                      <input
                        type="number"
                        value={config.seed}
                        onChange={(e) => updateField('seed', parseInt(e.target.value) || 42)}
                        className="flex-1 bg-[#050608] border border-[#1e212c] rounded px-2 py-1 font-mono text-[11px] text-slate-200"
                      />
                      <button
                        onClick={randomizeSeed}
                        title="Randomize seed"
                        className="p-1 rounded bg-[#151720] hover:bg-[#1e212c] text-slate-300 border border-[#272b3a]"
                      >
                        <RefreshCw className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* 2. Harvesting Profile Section */}
            {activeSection === 'harvesting' && (
              <div className="space-y-3">
                <div>
                  <label className="block text-[11px] font-medium text-slate-400 mb-1">
                    Ambient Energy Harvesting Regime
                  </label>
                  <select
                    id="select-harvesting-profile"
                    value={config.harvesting_profile}
                    onChange={(e) => updateField('harvesting_profile', e.target.value as HarvestingProfileType)}
                    className="w-full bg-[#050608] border border-[#1e212c] rounded px-2.5 py-1.5 text-slate-200 focus:border-slate-500 focus:outline-none cursor-pointer"
                  >
                    <option value="solar">Solar Diurnal Cycle (Day/Night + Clouds)</option>
                    <option value="shadowed_solar">Heterogeneous Shadowed Solar (Forest/Urban)</option>
                    <option value="stochastic">Stochastic Poisson Arrivals (RF/Thermal)</option>
                    <option value="constant">Constant Background Recharge</option>
                    <option value="trace">Real Solar Irradiance Trace (NREL GHI)</option>
                    <option value="none">None (Battery-Only Depletion Benchmark)</option>
                  </select>
                </div>

                {/* Profile specific parameters */}
                {(config.harvesting_profile === 'solar' || config.harvesting_profile === 'shadowed_solar' || config.harvesting_profile === 'trace') && (
                  <div className="p-2.5 rounded bg-[#050608] border border-[#1e212c] space-y-2.5">
                    <div>
                      <div className="flex justify-between text-[11px] mb-1">
                        <span className="text-slate-400">Peak Solar Rate (J/round):</span>
                        <span className="font-mono text-slate-300">{(config.solar_peak * 1000).toFixed(1)} mJ</span>
                      </div>
                      <input
                        type="range"
                        min={0.0005}
                        max={0.015}
                        step={0.0005}
                        value={config.solar_peak}
                        onChange={(e) => updateField('solar_peak', parseFloat(e.target.value))}
                        className="w-full accent-slate-400 cursor-pointer"
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <label className="block text-[10px] text-slate-400 mb-1">Diurnal Period (rds)</label>
                        <input
                          type="number"
                          min={6}
                          max={96}
                          step={2}
                          value={config.solar_period || 24}
                          onChange={(e) => updateField('solar_period', parseInt(e.target.value) || 24)}
                          className="w-full bg-[#090a0d] border border-[#1e212c] rounded px-2 py-1 font-mono text-[11px] text-slate-200"
                        />
                      </div>
                      <div>
                        <label className="block text-[10px] text-slate-400 mb-1">Daytime Fraction</label>
                        <input
                          type="number"
                          min={0.1}
                          max={0.9}
                          step={0.05}
                          value={config.solar_day_fraction || 0.5}
                          onChange={(e) => updateField('solar_day_fraction', parseFloat(e.target.value) || 0.5)}
                          className="w-full bg-[#090a0d] border border-[#1e212c] rounded px-2 py-1 font-mono text-[11px] text-slate-200"
                        />
                      </div>
                    </div>

                    {config.harvesting_profile === 'shadowed_solar' && (
                      <div>
                        <div className="flex justify-between text-[10px] mb-1">
                          <span className="text-slate-400">Shadow Occlusion Fraction:</span>
                          <span className="font-mono text-slate-300">{((config.shadow_fraction || 0.35) * 100).toFixed(0)}%</span>
                        </div>
                        <input
                          type="range"
                          min={0.1}
                          max={0.8}
                          step={0.05}
                          value={config.shadow_fraction || 0.35}
                          onChange={(e) => updateField('shadow_fraction', parseFloat(e.target.value))}
                          className="w-full accent-slate-400 cursor-pointer"
                        />
                      </div>
                    )}
                  </div>
                )}

                {config.harvesting_profile === 'stochastic' && (
                  <div className="p-2.5 rounded bg-[#050608] border border-[#1e212c] space-y-2.5">
                    <div>
                      <div className="flex justify-between text-[11px] mb-1">
                        <span className="text-slate-400">Poisson Arrival Rate (λ):</span>
                        <span className="font-mono text-slate-300">{config.stoch_lambda.toFixed(1)} / rd</span>
                      </div>
                      <input
                        type="range"
                        min={0.5}
                        max={10.0}
                        step={0.5}
                        value={config.stoch_lambda}
                        onChange={(e) => updateField('stoch_lambda', parseFloat(e.target.value))}
                        className="w-full accent-slate-400 cursor-pointer"
                      />
                    </div>
                    <div>
                      <div className="flex justify-between text-[11px] mb-1">
                        <span className="text-slate-400">Quantum Energy per Arrival:</span>
                        <span className="font-mono text-slate-300">{(config.stoch_quantum * 1000).toFixed(2)} mJ</span>
                      </div>
                      <input
                        type="range"
                        min={0.0005}
                        max={0.010}
                        step={0.0005}
                        value={config.stoch_quantum}
                        onChange={(e) => updateField('stoch_quantum', parseFloat(e.target.value))}
                        className="w-full accent-slate-400 cursor-pointer"
                      />
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* 3. Routing Engine Section */}
            {activeSection === 'routing' && (
              <div className="space-y-3">
                <div>
                  <label className="block text-[11px] font-medium text-slate-400 mb-1">
                    Multi-Hop Routing Algorithm
                  </label>
                  <select
                    id="select-routing-algorithm"
                    value={config.routing_algorithm}
                    onChange={(e) => updateField('routing_algorithm', e.target.value as RoutingAlgorithmType)}
                    className="w-full bg-[#050608] border border-[#1e212c] rounded px-2.5 py-1.5 text-slate-200 focus:border-slate-500 focus:outline-none cursor-pointer"
                  >
                    <option value="dijkstra">Dijkstra (Minimum Transmission Energy)</option>
                    <option value="energy_dijkstra">Energy-Aware Dijkstra (Residual-Weighted)</option>
                    <option value="astar">A* Heuristic Search (Euclidean to BS)</option>
                    <option value="dp_maximin">Maximin Bottleneck DP (Hop Constrained)</option>
                  </select>
                </div>

                {/* Adaptive Feature Toggles */}
                <div className="p-2.5 rounded bg-[#050608] border border-[#1e212c] space-y-2">
                  <div className="text-[11px] font-semibold text-slate-300 flex items-center gap-1.5">
                    <ShieldCheck className="w-3.5 h-3.5 text-slate-400" />
                    <span>Adaptive Optimization Toggles</span>
                  </div>

                  <label className="flex items-center gap-2 cursor-pointer pt-1">
                    <input
                      type="checkbox"
                      checked={!config.disable_time_dp}
                      onChange={(e) => updateField('disable_time_dp', !e.target.checked)}
                      className="rounded bg-[#090a0d] border-slate-700 text-slate-400 focus:ring-0 cursor-pointer"
                    />
                    <span className="text-[11px] text-slate-200">
                      Time-Augmented DP (dp[v][h][t])
                    </span>
                  </label>
                  <p className="text-[10px] text-slate-400 pl-5 leading-tight">
                    Projects incoming harvest recharge along future transmission arrival windows.
                  </p>

                  <label className="flex items-center gap-2 cursor-pointer pt-1">
                    <input
                      type="checkbox"
                      checked={!config.disable_harvesting_ch}
                      onChange={(e) => updateField('disable_harvesting_ch', !e.target.checked)}
                      className="rounded bg-[#090a0d] border-slate-700 text-slate-400 focus:ring-0 cursor-pointer"
                    />
                    <span className="text-[11px] text-slate-200">
                      EH-LEACH (Harvesting-Aware CH Election)
                    </span>
                  </label>
                  <p className="text-[10px] text-slate-400 pl-5 leading-tight">
                    Weights cluster head probability by projected residual energy.
                  </p>

                  <label className="flex items-center gap-2 cursor-pointer pt-1">
                    <input
                      type="checkbox"
                      checked={!config.disable_live_reroute}
                      onChange={(e) => updateField('disable_live_reroute', !e.target.checked)}
                      className="rounded bg-[#090a0d] border-slate-700 text-slate-400 focus:ring-0 cursor-pointer"
                    />
                    <span className="text-[11px] text-slate-200">
                      DSU Live Detour Recovery
                    </span>
                  </label>
                  <p className="text-[10px] text-slate-400 pl-5 leading-tight">
                    Instant Disjoint-Set Union local rerouting when intermediate relay exhausts energy.
                  </p>
                </div>

                <div>
                  <div className="flex justify-between text-[11px] mb-1">
                    <span className="text-slate-400">Max DP Hop Horizon (H):</span>
                    <span className="font-mono text-slate-300">{config.max_dp_hops} hops</span>
                  </div>
                  <input
                    type="range"
                    min={2}
                    max={10}
                    step={1}
                    value={config.max_dp_hops}
                    onChange={(e) => updateField('max_dp_hops', parseInt(e.target.value) || 5)}
                    className="w-full accent-slate-400 cursor-pointer"
                  />
                </div>
              </div>
            )}

            {/* 4. Advanced Physics Constants */}
            {activeSection === 'advanced' && (
              <div className="space-y-3">
                <div className="p-2.5 rounded bg-[#050608] border border-[#1e212c] space-y-2 text-[11px]">
                  <div className="font-semibold text-slate-300 flex items-center gap-1.5">
                    <Flame className="w-3.5 h-3.5 text-slate-400" />
                    <span>Radio Physical Parameters</span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-[10px]">
                    <div className="bg-[#090a0d] p-1.5 rounded border border-[#1e212c]">
                      <span className="text-slate-400 block">E_elec (Tx/Rx):</span>
                      <span className="font-mono text-slate-200">50.0 nJ / bit</span>
                    </div>
                    <div className="bg-[#090a0d] p-1.5 rounded border border-[#1e212c]">
                      <span className="text-slate-400 block">E_fs (Free Space):</span>
                      <span className="font-mono text-slate-200">10.0 pJ / bit / m²</span>
                    </div>
                    <div className="bg-[#090a0d] p-1.5 rounded border border-[#1e212c]">
                      <span className="text-slate-400 block">E_mp (Multipath):</span>
                      <span className="font-mono text-slate-200">0.0013 pJ / bit / m⁴</span>
                    </div>
                    <div className="bg-[#090a0d] p-1.5 rounded border border-[#1e212c]">
                      <span className="text-slate-400 block">Crossover (d₀):</span>
                      <span className="font-mono text-slate-200">87.71 meters</span>
                    </div>
                  </div>
                </div>

                <div>
                  <label className="block text-[11px] font-medium text-slate-400 mb-1">
                    Packet Payload Size (bits)
                  </label>
                  <input
                    type="number"
                    min={500}
                    max={16000}
                    step={500}
                    value={config.k_bits || 4000}
                    onChange={(e) => updateField('k_bits', parseInt(e.target.value) || 4000)}
                    className="w-full bg-[#050608] border border-[#1e212c] rounded px-2.5 py-1.5 font-mono text-slate-200 focus:border-slate-500 focus:outline-none"
                  />
                </div>
              </div>
            )}
          </div>

          {/* Action Trigger Footer */}
          <div className="p-3 bg-[#050608] border-t border-[#1b1d26] space-y-2">
            <button
              id="btn-run-simulation"
              onClick={onRunSimulation}
              disabled={loading}
              className={`w-full py-2 px-4 rounded font-semibold text-xs flex items-center justify-center gap-2 transition-colors ${
                loading
                  ? 'bg-[#151720] text-slate-500 cursor-not-allowed border border-[#222634]'
                  : 'bg-[#1c202c] hover:bg-[#262c3e] text-slate-100 active:bg-[#151822] border border-[#2b3348]'
              }`}
            >
              {loading ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Simulating...</span>
                </>
              ) : (
                <>
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>Run Simulation</span>
                </>
              )}
            </button>

            {loading && progressText && (
              <p className="text-[11px] text-center font-mono text-slate-300">
                {progressText}
              </p>
            )}
          </div>
        </>
      )}
    </aside>
  );
};

