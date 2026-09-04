import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { ControlPanel } from './components/ControlPanel';
import { NetworkTopologyView } from './components/NetworkTopologyView';
import { RoundScrubberView } from './components/RoundScrubberView';
import { EnergyHeatmapView } from './components/EnergyHeatmapView';
import { AnalyticsChartsView } from './components/AnalyticsChartsView';
import { BenchmarkSuiteView } from './components/BenchmarkSuiteView';
import { ExperimentsView } from './components/ExperimentsView';
import { TheoryDocsModal } from './components/TheoryDocsModal';
import { SavedRunsModal } from './components/SavedRunsModal';
import { useSimulation } from './hooks/useSimulation';
import { SimulationConfig, SimulationResults } from './types';
import { DEFAULT_CONFIG, PresetScenario } from './presets';
import { AlertCircle } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState<'network' | 'scrubber' | 'heatmap' | 'charts' | 'benchmark' | 'experiments'>('network');
  const [config, setConfig] = useState<SimulationConfig>(DEFAULT_CONFIG);
  const [currentRound, setCurrentRound] = useState<number>(0);
  const [isDocsOpen, setIsDocsOpen] = useState<boolean>(false);
  const [isSavedRunsOpen, setIsSavedRunsOpen] = useState<boolean>(false);

  const {
    loading,
    benchmarkLoading,
    progressText,
    error,
    results,
    setResults,
    benchmarkResults,
    runSimulation,
    runBenchmark
  } = useSimulation();

  // Initial simulation run on startup for instant visual feedback
  useEffect(() => {
    runSimulation(config);
  }, []);

  const handleSelectPreset = (preset: PresetScenario) => {
    const updated = { ...config, ...preset.config };
    setConfig(updated);
    runSimulation(updated);
  };

  const handleResetToDefaults = () => {
    setConfig(DEFAULT_CONFIG);
    runSimulation(DEFAULT_CONFIG);
  };

  const handleLoadSavedRun = (loadedResults: SimulationResults, loadedConfig: SimulationConfig) => {
    setConfig(loadedConfig);
    setResults(loadedResults);
    setCurrentRound(0);
  };

  return (
    <div className="min-h-screen bg-black text-slate-100 flex flex-col font-sans antialiased selection:bg-slate-800">
      {/* Top Navbar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onSelectPreset={handleSelectPreset}
        onOpenSavedRuns={() => setIsSavedRunsOpen(true)}
        onOpenDocs={() => setIsDocsOpen(true)}
        currentConfig={config}
        onResetToDefaults={handleResetToDefaults}
      />

      {/* Error notification banner */}
      {error && (
        <div className="bg-[#180a0d] border-b border-[#3b151b] px-4 py-2 text-xs text-rose-300 flex items-center justify-between">
          <div className="flex items-center gap-2 max-w-7xl mx-auto w-full">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* Main Workspace Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-3 sm:p-4 grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Left Sidebar: Simulation Configuration & Control Panel */}
        <div className="lg:col-span-4 xl:col-span-3 h-full">
          <ControlPanel
            config={config}
            onChangeConfig={setConfig}
            onRunSimulation={() => {
              setCurrentRound(0);
              runSimulation(config);
            }}
            loading={loading}
            progressText={progressText}
          />
        </div>

        {/* Right Main Content Area: Tab Views */}
        <div className="lg:col-span-8 xl:col-span-9 flex flex-col min-h-[560px]">
          {activeTab === 'network' && (
            <NetworkTopologyView
              results={results}
              config={config}
              currentRound={currentRound}
            />
          )}

          {activeTab === 'scrubber' && (
            <RoundScrubberView
              results={results}
              config={config}
              currentRound={currentRound}
              setCurrentRound={setCurrentRound}
            />
          )}

          {activeTab === 'heatmap' && (
            <EnergyHeatmapView
              results={results}
              config={config}
              currentRound={currentRound}
            />
          )}

          {activeTab === 'charts' && (
            <AnalyticsChartsView
              results={results}
              config={config}
            />
          )}

          {activeTab === 'benchmark' && (
            <BenchmarkSuiteView
              benchmarkResults={benchmarkResults}
              loading={benchmarkLoading}
              onRunBenchmark={() => runBenchmark(config.nodes, config.rounds, config.seed)}
              progressText={progressText}
            />
          )}

          {activeTab === 'experiments' && (
            <ExperimentsView />
          )}
        </div>
      </main>

      {/* Bottom Status Bar */}
      <footer className="border-t border-[#181a24] bg-[#050508] px-4 py-2 text-[11px] text-slate-400 font-mono">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1.5 text-slate-300">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              Engine: <span className="text-slate-200">Discrete-Event Ready</span>
            </span>
            <span className="text-slate-600">|</span>
            <span>Profile: <span className="text-slate-300">{config.harvesting_profile.replace('_', ' ').toUpperCase()}</span></span>
            <span className="text-slate-600 hidden sm:inline">|</span>
            <span className="hidden sm:inline">Radio: <span className="text-slate-300">E_elec=50nJ/b, d₀=87.7m</span></span>
          </div>
          <div className="flex items-center gap-3">
            <span>Nodes: <span className="text-slate-200">{config.nodes}</span></span>
            <span className="text-slate-600">|</span>
            <span>Rounds: <span className="text-slate-200">{config.rounds}</span></span>
            <span className="text-slate-600">|</span>
            <span>Seed: <span className="text-slate-200">{config.seed}</span></span>
          </div>
        </div>
      </footer>

      {/* Documentation & Mathematical Theory Modal */}
      <TheoryDocsModal
        isOpen={isDocsOpen}
        onClose={() => setIsDocsOpen(false)}
      />

      {/* Saved Runs & Local Storage Modal */}
      <SavedRunsModal
        isOpen={isSavedRunsOpen}
        onClose={() => setIsSavedRunsOpen(false)}
        onLoadRun={handleLoadSavedRun}
        currentResults={results}
        currentConfig={config}
      />
    </div>
  );
}

