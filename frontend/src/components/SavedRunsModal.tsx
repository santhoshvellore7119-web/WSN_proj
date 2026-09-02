import React, { useState, useEffect } from 'react';
import { X, FolderArchive, Play, Trash2, Calendar, HardDrive } from 'lucide-react';
import { SavedRun, SimulationResults, SimulationConfig } from '../types';

interface SavedRunsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLoadRun: (results: SimulationResults, config: SimulationConfig) => void;
  currentResults: SimulationResults | null;
  currentConfig: SimulationConfig;
}

export const SavedRunsModal: React.FC<SavedRunsModalProps> = ({
  isOpen,
  onClose,
  onLoadRun,
  currentResults,
  currentConfig
}) => {
  const [savedRuns, setSavedRuns] = useState<SavedRun[]>([]);
  const [saveName, setSaveName] = useState<string>('');

  useEffect(() => {
    try {
      const stored = localStorage.getItem('wsn_saved_runs');
      if (stored) {
        setSavedRuns(JSON.parse(stored));
      }
    } catch (e) {
      console.error(e);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSaveCurrent = () => {
    if (!currentResults) return;
    const name = saveName.trim() || `Run ${new Date().toLocaleTimeString()} (${currentConfig.nodes} nodes)`;
    const newRun: SavedRun = {
      id: 'run_' + Date.now(),
      name,
      createdAt: new Date().toLocaleString(),
      config: currentConfig,
      summary: currentResults.summary,
      results: currentResults
    };

    const updated = [newRun, ...savedRuns].slice(0, 10); // keep 10 latest
    setSavedRuns(updated);
    localStorage.setItem('wsn_saved_runs', JSON.stringify(updated));
    setSaveName('');
  };

  const handleDelete = (id: string) => {
    const updated = savedRuns.filter(r => r.id !== id);
    setSavedRuns(updated);
    localStorage.setItem('wsn_saved_runs', JSON.stringify(updated));
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85">
      <div className="bg-[#090a0d] border border-[#1b1d26] rounded max-w-2xl w-full max-h-[85vh] flex flex-col overflow-hidden shadow-2xl">
        {/* Header */}
        <div className="p-3 bg-[#050608] border-b border-[#1b1d26] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded bg-[#101218] border border-[#20232e] flex items-center justify-center text-slate-300">
              <FolderArchive className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-xs font-semibold text-slate-200">Saved Simulation Runs</h2>
              <p className="text-[10px] text-slate-400">
                Store and reload past experiment runs from browser storage
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded bg-[#101218] text-slate-400 hover:text-slate-200 hover:bg-[#181a24] border border-[#20232e] transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <div className="p-3.5 overflow-y-auto space-y-3 text-xs">
          {/* Save current run box */}
          {currentResults && (
            <div className="p-2.5 bg-[#050608] border border-[#1b1d26] rounded space-y-2">
              <span className="text-[11px] font-medium text-slate-300 block">
                Save Current Simulation Run
              </span>
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  placeholder="Run label (e.g. 100 Nodes Solar Diurnal DP)"
                  value={saveName}
                  onChange={(e) => setSaveName(e.target.value)}
                  className="flex-1 bg-[#07080a] border border-[#1c1e28] rounded px-2.5 py-1.5 text-slate-200 text-xs focus:border-[#2a2e3e] focus:outline-none"
                />
                <button
                  onClick={handleSaveCurrent}
                  className="py-1.5 px-3 rounded bg-[#181a24] hover:bg-[#202330] text-slate-200 border border-[#2a2e3e] font-medium text-xs flex items-center gap-1.5 transition-colors"
                >
                  <HardDrive className="w-3.5 h-3.5" />
                  <span>Save Run</span>
                </button>
              </div>
            </div>
          )}

          {/* List of saved runs */}
          <div className="space-y-2">
            <span className="text-[11px] font-medium text-slate-400 block">
              Saved Archives ({savedRuns.length})
            </span>

            {savedRuns.length === 0 ? (
              <p className="text-xs text-slate-500 italic py-4 text-center">
                No saved runs found in storage.
              </p>
            ) : (
              savedRuns.map((run) => (
                <div
                  key={run.id}
                  className="p-2.5 bg-[#050608] border border-[#1b1d26] rounded flex items-center justify-between gap-3 hover:border-[#2a2e3e] transition-colors"
                >
                  <div className="space-y-0.5">
                    <span className="font-medium text-slate-200 block text-xs">
                      {run.name}
                    </span>
                    <div className="flex items-center gap-2 text-[10px] text-slate-400 font-mono">
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {run.createdAt}
                      </span>
                      <span>•</span>
                      <span>{run.config.nodes} nodes</span>
                      <span>•</span>
                      <span className="text-slate-300">
                        FND: {run.summary.first_node_death_round ? `Rd ${run.summary.first_node_death_round}` : 'None'}
                      </span>
                      <span>•</span>
                      <span className="text-slate-300">
                        {run.summary.final_alive_nodes} alive
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-1.5">
                    {run.results && (
                      <button
                        onClick={() => {
                          onLoadRun(run.results!, run.config);
                          onClose();
                        }}
                        className="py-1 px-2.5 rounded bg-[#181a24] hover:bg-[#202330] text-slate-200 border border-[#2a2e3e] text-xs font-medium flex items-center gap-1 transition-colors"
                      >
                        <Play className="w-3 h-3 fill-current" />
                        <span>Load</span>
                      </button>
                    )}
                    <button
                      onClick={() => handleDelete(run.id)}
                      className="p-1.5 rounded bg-[#101218] hover:bg-[#221010] text-slate-400 hover:text-rose-300 border border-[#20232e] transition-colors"
                      title="Delete saved run"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="p-2.5 bg-[#050608] border-t border-[#1b1d26] flex justify-end">
          <button
            onClick={onClose}
            className="py-1 px-3.5 rounded bg-[#101218] hover:bg-[#181a24] text-slate-300 border border-[#20232e] text-xs transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

