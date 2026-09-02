import React, { useState, useEffect } from 'react';
import {
  Play,
  Pause,
  SkipBack,
  SkipForward,
  RotateCcw,
  Activity,
  Layers,
  CheckCircle2,
  XCircle
} from 'lucide-react';
import { SimulationResults, SimulationConfig } from '../types';

interface RoundScrubberViewProps {
  results: SimulationResults | null;
  config: SimulationConfig;
  currentRound: number;
  setCurrentRound: (r: number) => void;
}

export const RoundScrubberView: React.FC<RoundScrubberViewProps> = ({
  results,
  config,
  currentRound,
  setCurrentRound
}) => {
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1); // 1x, 2x, 5x, 10x

  const totalRounds = results ? results.time_series.rounds.length : config.rounds;
  const currentIdx = Math.min(Math.max(0, currentRound), Math.max(0, totalRounds - 1));

  // Auto-play timer
  useEffect(() => {
    let interval: any = null;
    if (isPlaying) {
      const delayMs = Math.max(25, 250 / playbackSpeed);
      interval = setInterval(() => {
        setCurrentRound((prev) => {
          if (prev >= totalRounds - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, delayMs);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isPlaying, playbackSpeed, totalRounds, setCurrentRound]);

  if (!results) {
    return (
      <div className="bg-[#090a0d] border border-[#1b1d26] rounded p-8 flex flex-col items-center justify-center text-center h-full min-h-[400px]">
        <div className="w-10 h-10 rounded bg-[#101218] border border-[#20232e] flex items-center justify-center text-slate-400 mb-3">
          <Activity className="w-5 h-5" />
        </div>
        <h3 className="text-xs font-semibold text-slate-200 mb-1">No Simulation Data Available</h3>
        <p className="text-[11px] text-slate-400 max-w-sm">
          Run a simulation from the left control panel to inspect step-by-step round metrics and routing playback.
        </p>
      </div>
    );
  }

  const ts = results.time_series;
  const dt = results.detailed_data;

  const roundNum = ts.rounds[currentIdx] || currentIdx + 1;
  const aliveNodes = ts.alive_nodes[currentIdx] ?? config.nodes;
  const harvestedEnergy = ts.harvested_energy[currentIdx] ?? 0;
  const consumedEnergy = ts.consumed_energy[currentIdx] ?? 0;
  const fairness = ts.fairness_index[currentIdx] ?? 1.0;
  const pdr = ts.pdr_history[currentIdx] ?? 1.0;

  const chList = dt.cluster_heads_history[currentIdx] || [];
  const activeRoutes = dt.routes_history[currentIdx] || {};

  return (
    <div className="bg-[#090a0d] border border-[#1b1d26] rounded flex flex-col h-full overflow-hidden space-y-4 p-4">
      {/* Top Playback Control Deck */}
      <div className="bg-[#050608] border border-[#1b1d26] p-3 rounded space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">Playback Status</span>
            <div className="flex items-baseline gap-2">
              <span className="text-xl font-bold font-mono text-slate-200">
                Round {roundNum}
              </span>
              <span className="text-xs font-mono text-slate-400">
                / {totalRounds} total
              </span>
            </div>
          </div>

          {/* Transport Controls */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                setIsPlaying(false);
                setCurrentRound(0);
              }}
              title="Jump to Start"
              className="p-1.5 rounded bg-[#101218] hover:bg-[#181a24] text-slate-300 border border-[#20232e] transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>

            <button
              onClick={() => {
                setIsPlaying(false);
                setCurrentRound(Math.max(0, currentIdx - 1));
              }}
              title="Previous Round"
              className="p-1.5 rounded bg-[#101218] hover:bg-[#181a24] text-slate-300 border border-[#20232e] transition-colors"
            >
              <SkipBack className="w-3.5 h-3.5" />
            </button>

            <button
              onClick={() => setIsPlaying(!isPlaying)}
              title={isPlaying ? 'Pause Playback' : 'Play Simulation'}
              className={`px-3 py-1.5 rounded font-semibold text-xs flex items-center gap-1.5 transition-all ${
                isPlaying
                  ? 'bg-[#2a3040] hover:bg-[#343b4e] text-slate-100 border border-[#3e475c]'
                  : 'bg-[#181a24] hover:bg-[#222532] text-slate-100 border border-[#2a2e3e]'
              }`}
            >
              {isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5 fill-current" />}
              <span>{isPlaying ? 'Pause' : 'Play'}</span>
            </button>

            <button
              onClick={() => {
                setIsPlaying(false);
                setCurrentRound(Math.min(totalRounds - 1, currentIdx + 1));
              }}
              title="Next Round"
              className="p-1.5 rounded bg-[#101218] hover:bg-[#181a24] text-slate-300 border border-[#20232e] transition-colors"
            >
              <SkipForward className="w-3.5 h-3.5" />
            </button>

            {/* Speed selector */}
            <div className="flex items-center bg-[#07080a] p-0.5 rounded border border-[#1c1e28] text-xs">
              {[1, 2, 5, 10].map((spd) => (
                <button
                  key={spd}
                  onClick={() => setPlaybackSpeed(spd)}
                  className={`px-2 py-0.5 rounded text-[10px] font-mono transition-colors ${
                    playbackSpeed === spd
                      ? 'bg-[#181a24] text-slate-100 font-semibold border border-[#2a2e3e]'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {spd}x
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Scrubber Progress Bar */}
        <div className="space-y-1">
          <input
            type="range"
            min={0}
            max={Math.max(0, totalRounds - 1)}
            value={currentIdx}
            onChange={(e) => {
              setIsPlaying(false);
              setCurrentRound(parseInt(e.target.value) || 0);
            }}
            className="w-full accent-slate-400 cursor-pointer h-1.5 bg-[#12141c] rounded"
          />
          <div className="flex justify-between text-[10px] font-mono text-slate-400">
            <span>Round 1</span>
            <span>FND: {results.summary.first_node_death_round ? `Rd ${results.summary.first_node_death_round}` : 'None'}</span>
            <span>HND: {results.summary.half_nodes_dead_round ? `Rd ${results.summary.half_nodes_dead_round}` : 'None'}</span>
            <span>Round {totalRounds}</span>
          </div>
        </div>
      </div>

      {/* Metric Telemetry Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
        <div className="bg-[#050608] border border-[#1b1d26] p-2.5 rounded">
          <span className="text-[10px] text-slate-400 block font-medium">Alive Sensors</span>
          <div className="flex items-baseline gap-1 mt-0.5">
            <span className="text-base font-bold font-mono text-slate-200">{aliveNodes}</span>
            <span className="text-[10px] font-mono text-slate-400">/ {config.nodes}</span>
          </div>
          <span className="text-[10px] text-slate-400 font-mono">
            {((aliveNodes / config.nodes) * 100).toFixed(1)}% alive
          </span>
        </div>

        <div className="bg-[#050608] border border-[#1b1d26] p-2.5 rounded">
          <span className="text-[10px] text-slate-400 block font-medium">Active CHs</span>
          <div className="flex items-baseline gap-1 mt-0.5">
            <span className="text-base font-bold font-mono text-slate-200">{chList.length}</span>
            <span className="text-[10px] font-mono text-slate-400">clusters</span>
          </div>
          <span className="text-[10px] text-slate-400 font-mono">
            {aliveNodes > 0 ? ((chList.length / aliveNodes) * 100).toFixed(1) : 0}% of alive
          </span>
        </div>

        <div className="bg-[#050608] border border-[#1b1d26] p-2.5 rounded">
          <span className="text-[10px] text-slate-400 block font-medium">Harvested (Rd)</span>
          <div className="flex items-baseline gap-1 mt-0.5">
            <span className="text-base font-bold font-mono text-slate-200">
              {(harvestedEnergy * 1000).toFixed(1)}
            </span>
            <span className="text-[10px] font-mono text-slate-400">mJ</span>
          </div>
          <span className="text-[10px] text-slate-400 font-mono">inflow</span>
        </div>

        <div className="bg-[#050608] border border-[#1b1d26] p-2.5 rounded">
          <span className="text-[10px] text-slate-400 block font-medium">Consumed (Rd)</span>
          <div className="flex items-baseline gap-1 mt-0.5">
            <span className="text-base font-bold font-mono text-slate-200">
              {(consumedEnergy * 1000).toFixed(1)}
            </span>
            <span className="text-[10px] font-mono text-slate-400">mJ</span>
          </div>
          <span className="text-[10px] text-slate-400 font-mono">tx/rx/agg</span>
        </div>

        <div className="bg-[#050608] border border-[#1b1d26] p-2.5 rounded">
          <span className="text-[10px] text-slate-400 block font-medium">Delivery (PDR)</span>
          <div className="flex items-baseline gap-1 mt-0.5">
            <span className="text-base font-bold font-mono text-slate-200">
              {(pdr * 100).toFixed(1)}%
            </span>
          </div>
          <span className="text-[10px] text-slate-400 font-mono">packet success</span>
        </div>

        <div className="bg-[#050608] border border-[#1b1d26] p-2.5 rounded">
          <span className="text-[10px] text-slate-400 block font-medium">Jain's Fairness</span>
          <div className="flex items-baseline gap-1 mt-0.5">
            <span className="text-base font-bold font-mono text-slate-200">
              {fairness.toFixed(3)}
            </span>
          </div>
          <span className="text-[10px] text-slate-400 font-mono">equality</span>
        </div>
      </div>

      {/* Cluster Head Routing Breakdown for Active Round */}
      <div className="bg-[#050608] border border-[#1b1d26] rounded p-3 space-y-2">
        <div className="flex items-center justify-between pb-1 border-b border-[#1b1d26]">
          <div className="flex items-center gap-2">
            <Layers className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-xs font-semibold text-slate-200">
              Cluster Heads & Multi-Hop Routes (Round {roundNum})
            </span>
          </div>
          <span className="text-[10px] font-mono text-slate-400">
            {Object.keys(activeRoutes).length} active routes
          </span>
        </div>

        {chList.length === 0 ? (
          <p className="text-xs text-slate-500 italic py-2">
            No active cluster heads in this round.
          </p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-h-48 overflow-y-auto pr-1">
            {chList.map((chId) => {
              const routeInfo = activeRoutes[chId];
              const path = routeInfo ? routeInfo[0] : null;
              const cost = routeInfo ? routeInfo[1] : 0;
              const hasPath = path && path.length > 0;

              return (
                <div
                  key={`ch-card-${chId}`}
                  className="bg-[#090a0d] border border-[#1b1d26] rounded p-2 text-xs space-y-1.5 flex flex-col justify-between"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-200 font-mono flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-[#925807]"></span>
                      Cluster Head #{chId}
                    </span>
                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-mono flex items-center gap-1 ${
                      hasPath ? 'bg-[#0f1f17] text-[#86efac] border border-[#1b3d29]' : 'bg-[#200f0f] text-[#fca5a5] border border-[#3d1818]'
                    }`}>
                      {hasPath ? <CheckCircle2 className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
                      {hasPath ? `${path.length - 1} hops` : 'No Path'}
                    </span>
                  </div>

                  <div className="text-[10px] font-mono text-slate-300 bg-[#050608] p-1.5 rounded border border-[#181a24] flex items-center gap-1 overflow-x-auto">
                    <span className="text-amber-500">CH-{chId}</span>
                    {path && path.slice(1).map((hopNode, idx) => (
                      <React.Fragment key={idx}>
                        <span className="text-slate-500">→</span>
                        <span className={hopNode === -1 ? 'text-red-400 font-bold' : 'text-slate-300'}>
                          {hopNode === -1 ? 'BaseStation' : `Node-${hopNode}`}
                        </span>
                      </React.Fragment>
                    ))}
                  </div>

                  <div className="flex justify-between text-[10px] text-slate-400 font-mono">
                    <span>Path Energy Metric:</span>
                    <span className="text-slate-300">{(cost * 1000).toFixed(3)} mJ</span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

