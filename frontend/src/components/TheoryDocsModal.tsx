import React from 'react';
import { X, BookOpen, Cpu, Zap, Flame, ShieldCheck } from 'lucide-react';

interface TheoryDocsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const TheoryDocsModal: React.FC<TheoryDocsModalProps> = ({
  isOpen,
  onClose
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85">
      <div className="bg-[#090a0d] border border-[#1b1d26] rounded max-w-4xl w-full max-h-[90vh] flex flex-col overflow-hidden shadow-2xl">
        {/* Header */}
        <div className="p-3 bg-[#050608] border-b border-[#1b1d26] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded bg-[#101218] border border-[#20232e] flex items-center justify-center text-slate-300">
              <BookOpen className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-xs font-semibold text-slate-200">
                Mathematical Foundations & Algorithmic Theory
              </h2>
              <p className="text-[10px] text-slate-400">
                Physics of Energy Harvesting WSNs • Time-Augmented DP • EH-LEACH • DSU Live Detours
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

        {/* Scrollable Content */}
        <div className="p-5 overflow-y-auto space-y-4 text-xs text-slate-300 leading-relaxed">
          {/* Section 1: First-Order Radio Model */}
          <div className="space-y-2 p-3 rounded bg-[#050608] border border-[#1b1d26]">
            <div className="flex items-center gap-2 text-slate-200 font-semibold text-xs">
              <Flame className="w-4 h-4 text-slate-400" />
              <span>1. First-Order Radio Transmission & Reception Model</span>
            </div>
            <p className="text-slate-400">
              Energy consumed to transmit a $k$-bit message across Euclidean distance $d$ follows the standard Heinzelman / LEACH first-order radio propagation model:
            </p>
            <div className="bg-[#07080a] p-2.5 rounded border border-[#181a24] font-mono text-[11px] text-slate-300 space-y-1">
              <div>E_Tx(k, d) = k · E_elec + k · ε_fs · d²   (if d &lt; d₀)</div>
              <div>E_Tx(k, d) = k · E_elec + k · ε_mp · d⁴   (if d ≥ d₀)</div>
              <div>E_Rx(k)    = k · E_elec</div>
            </div>
            <p className="text-slate-400">
              Where the crossover distance d₀ = √(ε_fs / ε_mp) ≈ 87.71 meters.
              Aggregating M data packets into an aggregated cluster summary consumes E_DA = 5 nJ/bit/signal.
            </p>
          </div>

          {/* Section 2: EH-LEACH */}
          <div className="space-y-2 p-3 rounded bg-[#050608] border border-[#1b1d26]">
            <div className="flex items-center gap-2 text-slate-200 font-semibold text-xs">
              <Zap className="w-4 h-4 text-slate-400" />
              <span>2. EH-LEACH: Energy-Harvesting Aware Cluster Head Election</span>
            </div>
            <p className="text-slate-400">
              Standard LEACH elects cluster heads based purely on probability $p$ and round index $r \bmod (1/p)$. In an energy-harvesting environment with spatial heterogeneity, classical LEACH causes premature node death in shaded regions.
            </p>
            <p className="text-slate-400">
              EH-LEACH weights the election probability dynamically by the projected next-round residual energy including harvest inflow:
            </p>
            <div className="bg-[#07080a] p-2.5 rounded border border-[#181a24] font-mono text-[11px] text-slate-300">
              <div>T(n) = [ p / (1 - p · (r mod 1/p)) ] · [ (E_residual(n) + E_harvest_est(n)) / E_max ]</div>
            </div>
            <p className="text-slate-400">
              Nodes in sunlit zones or with high battery buffers are prioritized to take on the high-energy CH transmission burden, balancing spatial network longevity.
            </p>
          </div>

          {/* Section 3: Time-Augmented DP */}
          <div className="space-y-2 p-3 rounded bg-[#050608] border border-[#1b1d26]">
            <div className="flex items-center gap-2 text-slate-200 font-semibold text-xs">
              <Cpu className="w-4 h-4 text-slate-400" />
              <span>3. Time-Augmented Dynamic Programming ($dp[v][h][t]$)</span>
            </div>
            <p className="text-slate-400">
              Standard Dijkstra computes paths using instantaneous residual energy at time $t=0$, which ignores incoming solar recharge during multi-hop transmission delays.
            </p>
            <p className="text-slate-400">
              Our Time-Augmented DP engine evaluates future energy states across a bounded hop horizon $H$ and arrival time windows $t$:
            </p>
            <div className="bg-[#07080a] p-2.5 rounded border border-[#181a24] font-mono text-[11px] text-slate-300">
              <div>dp[v][h][t] = max(u ∈ N(v)) min( dp[u][h-1][t + Δt] + E_harvest(v, t) - E_Tx(v, u), E_max )</div>
            </div>
            <p className="text-slate-400">
              This allows forwarding packets through relays that may be momentarily low on energy but are projected to receive strong solar replenishment by the time the packet queue reaches them.
            </p>
          </div>

          {/* Section 4: DSU Live Detour Recovery */}
          <div className="space-y-2 p-3 rounded bg-[#050608] border border-[#1b1d26]">
            <div className="flex items-center gap-2 text-slate-200 font-semibold text-xs">
              <ShieldCheck className="w-4 h-4 text-slate-400" />
              <span>4. Disjoint-Set Union (DSU) Live Detour Recovery</span>
            </div>
            <p className="text-slate-400">
              When an intermediate relay node depletes its battery mid-round, global path recalculation incurs high runtime overhead.
            </p>
            <p className="text-slate-400">
              Our engine maintains a dynamic Disjoint-Set Union structure with path compression and union-by-rank. When a relay link fails:
            </p>
            <ul className="list-disc pl-5 space-y-1 text-slate-400">
              <li>The node queries for the nearest viable connected component.</li>
              <li>A local detour is established in amortized O(α(N)) time without network-wide re-clustering.</li>
            </ul>
          </div>
        </div>

        {/* Footer */}
        <div className="p-2.5 bg-[#050608] border-t border-[#1b1d26] flex justify-end">
          <button
            onClick={onClose}
            className="py-1 px-3.5 rounded bg-[#181a24] hover:bg-[#202330] text-slate-200 border border-[#2a2e3e] text-xs font-medium transition-colors"
          >
            Close Documentation
          </button>
        </div>
      </div>
    </div>
  );
};

