import React from 'react';
import {
  Activity,
  Zap,
  BookOpen,
  FolderArchive,
  BarChart3,
  SlidersHorizontal,
  Layers,
  FlaskConical,
  RotateCcw
} from 'lucide-react';
import { PRESET_SCENARIOS, PresetScenario } from '../engine/presets';
import { SimulationConfig } from '../types';

interface NavbarProps {
  activeTab: 'network' | 'scrubber' | 'heatmap' | 'charts' | 'benchmark' | 'experiments';
  setActiveTab: (tab: 'network' | 'scrubber' | 'heatmap' | 'charts' | 'benchmark' | 'experiments') => void;
  onSelectPreset: (preset: PresetScenario) => void;
  onOpenSavedRuns: () => void;
  onOpenDocs: () => void;
  currentConfig: SimulationConfig;
  onResetToDefaults: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  onSelectPreset,
  onOpenSavedRuns,
  onOpenDocs,
  currentConfig,
  onResetToDefaults
}) => {
  return (
    <header className="bg-black border-b border-[#181a24] sticky top-0 z-30 px-4 py-2.5">
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3">
        
        {/* Brand & Identity */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded bg-[#0d0e12] border border-[#222530] flex items-center justify-center text-slate-300">
            <Activity className="w-4 h-4 text-slate-300" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-sm font-semibold text-slate-100 tracking-tight">
                WSN Energy-Harvesting Simulator
              </h1>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-[#101218] text-slate-400 border border-[#222530]">
                v2.4 Core
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-normal">
              Discrete Event Simulator • Time-Augmented DP • EH-LEACH • DSU Rerouting
            </p>
          </div>
        </div>

        {/* View Switcher Tabs */}
        <nav className="flex items-center bg-[#070709] p-0.5 rounded border border-[#1c1e28] text-xs font-medium">
          <button
            id="tab-network-topology"
            onClick={() => setActiveTab('network')}
            className={`px-3 py-1.5 rounded flex items-center gap-1.5 transition-colors ${
              activeTab === 'network'
                ? 'bg-[#1c1f2a] text-slate-100 font-semibold border border-[#2b3042]'
                : 'text-slate-400 hover:text-slate-200 hover:bg-[#101218]'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>Topology</span>
          </button>

          <button
            id="tab-round-scrubber"
            onClick={() => setActiveTab('scrubber')}
            className={`px-3 py-1.5 rounded flex items-center gap-1.5 transition-colors ${
              activeTab === 'scrubber'
                ? 'bg-[#1c1f2a] text-slate-100 font-semibold border border-[#2b3042]'
                : 'text-slate-400 hover:text-slate-200 hover:bg-[#101218]'
            }`}
          >
            <SlidersHorizontal className="w-3.5 h-3.5" />
            <span>Playback</span>
          </button>

          <button
            id="tab-energy-heatmap"
            onClick={() => setActiveTab('heatmap')}
            className={`px-3 py-1.5 rounded flex items-center gap-1.5 transition-colors ${
              activeTab === 'heatmap'
                ? 'bg-[#1c1f2a] text-slate-100 font-semibold border border-[#2b3042]'
                : 'text-slate-400 hover:text-slate-200 hover:bg-[#101218]'
            }`}
          >
            <Zap className="w-3.5 h-3.5" />
            <span>Heatmap</span>
          </button>

          <button
            id="tab-analytics-charts"
            onClick={() => setActiveTab('charts')}
            className={`px-3 py-1.5 rounded flex items-center gap-1.5 transition-colors ${
              activeTab === 'charts'
                ? 'bg-[#1c1f2a] text-slate-100 font-semibold border border-[#2b3042]'
                : 'text-slate-400 hover:text-slate-200 hover:bg-[#101218]'
            }`}
          >
            <BarChart3 className="w-3.5 h-3.5" />
            <span>Analytics</span>
          </button>

          <button
            id="tab-benchmark-suite"
            onClick={() => setActiveTab('benchmark')}
            className={`px-3 py-1.5 rounded flex items-center gap-1.5 transition-colors ${
              activeTab === 'benchmark'
                ? 'bg-[#1c1f2a] text-slate-100 font-semibold border border-[#2b3042]'
                : 'text-slate-400 hover:text-slate-200 hover:bg-[#101218]'
            }`}
          >
            <Activity className="w-3.5 h-3.5" />
            <span>Benchmarks</span>
          </button>

          <button
            id="tab-experiments-sweeps"
            onClick={() => setActiveTab('experiments')}
            className={`px-3 py-1.5 rounded flex items-center gap-1.5 transition-colors ${
              activeTab === 'experiments'
                ? 'bg-[#1c1f2a] text-slate-100 font-semibold border border-[#2b3042]'
                : 'text-slate-400 hover:text-slate-200 hover:bg-[#101218]'
            }`}
          >
            <FlaskConical className="w-3.5 h-3.5" />
            <span>Experiments</span>
          </button>
        </nav>

        {/* Action Controls & Presets */}
        <div className="flex items-center gap-2">
          {/* Preset Selector */}
          <div className="flex items-center gap-1.5 bg-[#08090c] px-2.5 py-1.5 rounded border border-[#1e202a]">
            <span className="text-[11px] text-slate-400">Preset:</span>
            <select
              id="preset-selector-dropdown"
              className="bg-transparent text-xs text-slate-200 focus:outline-none cursor-pointer"
              onChange={(e) => {
                const p = PRESET_SCENARIOS.find(x => x.id === e.target.value);
                if (p) onSelectPreset(p);
              }}
              defaultValue="default"
            >
              {PRESET_SCENARIOS.map((p) => (
                <option key={p.id} value={p.id} className="bg-[#0e1014] text-slate-200">
                  {p.name}
                </option>
              ))}
            </select>
          </div>

          <button
            id="btn-open-saved-runs"
            onClick={onOpenSavedRuns}
            title="Saved simulation runs"
            className="p-1.5 rounded bg-[#0d0e12] hover:bg-[#181a22] text-slate-300 border border-[#20232e] text-xs flex items-center gap-1 transition-colors"
          >
            <FolderArchive className="w-3.5 h-3.5 text-slate-400" />
            <span className="hidden sm:inline">Saved</span>
          </button>

          <button
            id="btn-open-theory-docs"
            onClick={onOpenDocs}
            title="Formulation & Mathematical Specification"
            className="p-1.5 rounded bg-[#0d0e12] hover:bg-[#181a22] text-slate-300 border border-[#20232e] text-xs flex items-center gap-1 transition-colors"
          >
            <BookOpen className="w-3.5 h-3.5 text-slate-400" />
            <span className="hidden sm:inline">Theory</span>
          </button>

          <button
            id="btn-reset-defaults"
            onClick={onResetToDefaults}
            title="Reset to default settings"
            className="p-1.5 rounded bg-[#0d0e12] hover:bg-[#181a22] text-slate-400 hover:text-slate-200 border border-[#20232e] text-xs transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>

      </div>
    </header>
  );
};

