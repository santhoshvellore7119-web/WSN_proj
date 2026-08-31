# WSN Energy-Harvesting Routing Simulator

A 2nd-year B.Tech Data Structures & Algorithms course project exploring adaptive routing in Wireless Sensor Networks (WSNs) with ambient energy harvesting.

## 🚀 Enhanced Version Available!

An enhanced version of this simulator is now available with a **REST API backend** and **React frontend** for interactive simulation configuration, visualization, and benchmarking. Features include:

- **Web-based interface** for real-time parameter adjustment and results visualization
- **REST API** for programmatic access and automation  
- **Persistence layer** (SQLite) to save and compare simulation runs
- **Interactive visualizations**: network topology, time-series charts, and energy heatmaps
- **One-click benchmarking** to run standard comparison scenarios

To use the enhanced version, see the [`backend/`](../tree/main/backend) and [`frontend/`](../tree/main/frontend) directories, or read the [Enhanced Version README](../README_ENHANCED.md) for detailed setup instructions.

The core simulator in [`src/`](../tree/main/src) remains unchanged and fully functional via the original CLI.

---

## About the Project

In standard sensor networks, nodes run on non-rechargeable batteries, so residual energy only goes down over time. Protocols like LEACH, Dijkstra, and classical bottleneck DP make sense here because once a node is low on battery, you should avoid routing traffic through it.

However, when nodes are equipped with energy harvesters (like solar cells or ambient RF harvesters), battery levels are **non-monotonic**—a node with low battery right now might recharge in a few time steps. If we only look at instantaneous battery levels, we end up ignoring nodes that would be perfectly good relays by the time a packet actually arrives.

This project implements a round-based WSN simulator in Python to study how routing and clustering can take advantage of incoming harvested energy.

### What We Implemented:
1. **Time-Augmented Maximin DP (`dp[v][h][t]`):** An extension of bottleneck dynamic programming with a discrete arrival time dimension $t$. Instead of only checking static energy at round start, it projects future recharge so packets can route through nodes that recharge just-in-time.
2. **Energy-Aware Dijkstra Baseline (MBCR):** A strong energy-aware baseline where edge transmission costs are inversely weighted by the receiver's residual battery level.
3. **Harvesting-Aware LEACH Clustering:** Modifies the standard LEACH cluster head election threshold to account for expected energy harvest over the round.
4. **Union-Find (DSU) Live Detour Rerouting:** Uses Disjoint-Set Union with path compression and rank optimization to quickly find a local detour around a dying relay node mid-round ($6.1\times$ faster than full DP recomputation).
5. **Harvesting Profiles:** Implements diurnal day/night solar cycles, building shadow/canopy occlusion, RF power transfer hotspots, and stochastic Poisson arrivals.

---

## Minimal 5-Node Adversarial Counterexample

To isolate the mechanism without simulation noise, we constructed a minimal 5-node topology where Classical Maximin DP and Energy-Aware Dijkstra provably fail, and Time-Augmented DP provably succeeds:

```
        [Node 1: Relay A (Depleting)]
        E(0) = 0.030 J, H = +0.000 J/step
               /                 \
              /                   \
             /                     \
[Node 0: Source S]               [Node -1: Sink BS]
E(0) = 0.050 J                   (Unlimited Energy)
             \                     /
              \                   /
               \                 /
        [Node 2: Relay B (Recharging)]
        E(0) = 0.005 J, H = +0.035 J/step
```

- **Classical Maximin DP:** Sees $E_1(0) = 0.030\text{ J} > E_2(0) = 0.005\text{ J}$ at $t=0$, picking Path `[0, 1, -1]`. Relay $1$ receives zero harvest, burns out, and partitions the route.
- **Energy-Aware Dijkstra:** Penalizes Relay $2$ due to its low initial energy ($0.005\text{ J}$), picking Path `[0, 1, -1]`.
- **Time-Augmented DP (Ours):** Projects Relay $2$'s arrival energy at $t=1$: $E_{\text{proj}}(2, 1) = 0.005 + 0.035 = 0.040\text{ J} > 0.030\text{ J}$, successfully routing via `[0, 2, -1]`.

Run the counterexample directly:
```bash
python run_counterexample.py
```

---

## Formal Asymptotic Complexity Analysis

| Routing Algorithm | Time Complexity (Per Source) | Space Complexity | State Space Structure | Substructure / Principle of Optimality |
| :--- | :--- | :--- | :--- | :--- |
| **Dijkstra (Shortest Radio Cost)** | $O((|E| + |V|) \log |V|)$ | $O(|V|)$ | $1\text{D Table } dist[v]$ | Optimal on additive static non-negative edge costs |
| **Energy-Aware Dijkstra (MBCR)** | $O((|E| + |V|) \log |V|)$ | $O(|V|)$ | $1\text{D Table } dist[v]$ | Optimal on static residual-energy-penalized edge weights |
| **Classical Maximin DP** | $O(|E| \cdot H)$ | $O(|V| \cdot H)$ | $2\text{D Table } dp[v][h]$ | Optimal for static bottleneck capacity over $H$ hops |
| **Time-Augmented DP ($dp[v][h][t]$)** | $O(|E| \cdot H \cdot T)$ | $O(|V| \cdot H \cdot T)$ | $3\text{D Table } dp[v][h][t]$ | Globally optimal on Time-Expanded DAG |
| **Union-Find (DSU) Live Detour** | $O(|E| \cdot \alpha(|V|))$ init / $O(1)$ query | $O(|V|)$ | $1\text{D Disjoint-Set Arrays}$ | Instantaneous reachability partition invariant |

---

## Theoretical Optimality & Approximation Bounds

1. **Bellman Optimality on Time-Expanded DAG:**
   The 3D state recurrence $\text{dp}[v][h][t] = \max_{u} \min(\text{dp}[u][h-1][t-\delta], E_{\text{proj}}(v, t))$ operates on a strictly acyclic time-expanded DAG $\mathcal{G}_T$. Because $\min(a, c)$ is associative and monotonic, optimal substructure holds, yielding exact globally optimal maximin bottleneck paths.
2. **$\epsilon$-Approximation Bound under Bounded Stochastic Harvest:**
   If stochastic harvesting noise is bounded by $|\xi_v(t)| \le \epsilon$, the bottleneck capacity of the path chosen by Time-Augmented DP is guaranteed to be within $2\epsilon$ of an omniscient offline oracle:
   $$B(P_{\text{Time-DP}}) \ge B(P^*) - 2\epsilon$$

---

## Experimental Results

### 1. Canonical Single-Seed Benchmark (Seed 42, 50 Nodes, 350 Rounds)

| Configuration | First Node Death (FND) | Half Nodes Dead (HND) | Alive Nodes (Round 350) | Total Residual Energy |
| :--- | :--- | :--- | :--- | :--- |
| **1. Baseline (No Harvesting)** | Round 82 | Round 112 | 0 / 50 | 0.0000 J |
| **2. Solar (Unaware Dijkstra)** | Round 165 | Round 209 | 0 / 50 | 0.0000 J |
| **3. Solar (Energy-Aware Dijkstra)** | Round 165 | Round 209 | 0 / 50 | 0.0000 J |
| **4. Solar (Adaptive Time-DP)** | Round 165 | Round 208 | 0 / 50 | 0.0000 J |
| **5. Shadowed (Unaware Dijkstra)** | Round 108 | $> 350$ | 27 / 50 | 0.8142 J |
| **6. Shadowed (Energy-Aware Dijkstra)** | Round 108 | $> 350$ | 27 / 50 | 0.8142 J |
| **7. Shadowed (Adaptive Time-DP)** | **Round 109** | $> 350$ | **27 / 50** | 0.7995 J |
| **8. Stochastic (Unaware Dijkstra)** | Round 320 | $> 350$ | 40 / 50 | 0.2581 J |
| **9. Stochastic (Adaptive Time-DP)** | **Round 329** | $> 350$ | **41 / 50** | 0.2532 J |

---

### 2. Multi-Seed Statistical Validation ($N = 5$ Independent Topologies)

Tested across random seeds `[42, 7, 123, 256, 999]`:

| Configuration | FND ($\mu \pm \sigma$) | HND ($\mu \pm \sigma$) | Alive Nodes ($\mu \pm \sigma$) | Total Energy ($\mu \pm \sigma$) |
| :--- | :--- | :--- | :--- | :--- |
| **Baseline (No Harvesting)** | $83.0 \pm 3.9$ | $110.2 \pm 1.3$ | $0.0 \pm 0.0$ | $0.0000 \pm 0.0000\text{ J}$ |
| **Solar (Unaware Dijkstra)** | $160.6 \pm 3.6$ | $207.0 \pm 4.7$ | $0.2 \pm 0.4$ | $0.0036 \pm 0.0080\text{ J}$ |
| **Solar (Energy-Aware Dijkstra)** | $160.6 \pm 3.6$ | $207.0 \pm 4.7$ | $0.2 \pm 0.4$ | $0.0036 \pm 0.0080\text{ J}$ |
| **Solar (Adaptive Time-DP)** | $159.6 \pm 4.9$ | $207.0 \pm 4.7$ | $0.2 \pm 0.4$ | $0.0036 \pm 0.0080\text{ J}$ |
| **Shadowed (Unaware Dijkstra)** | $105.0 \pm 4.7$ | $> 350$ | $23.8 \pm 3.1$ | $0.5026 \pm 0.2325\text{ J}$ |
| **Shadowed (Energy-Aware Dijkstra)** | $105.0 \pm 4.7$ | $> 350$ | $23.8 \pm 3.1$ | $0.5026 \pm 0.2325\text{ J}$ |
| **Shadowed (Adaptive Time-DP)** | **$105.4 \pm 5.0$** | $> 350$ | **$23.8 \pm 3.1$** | $0.4994 \pm 0.2317\text{ J}$ |
| **Stochastic (Unaware Dijkstra)** | $280.2 \pm 32.4$ | $> 350$ | $38.8 \pm 3.3$ | $0.1998 \pm 0.0596\text{ J}$ |
| **Stochastic (Adaptive Time-DP)** | $280.0 \pm 43.3$ | $> 350$ | $37.8 \pm 4.0$ | $0.2004 \pm 0.0616\text{ J}$ |

---

### 3. DSU Live Detour Speedup Benchmark ($N = 500$ Trials)

- **DSU Local Detour Latency:** $4.00\text{ ms}$ ($100\%$ recovery success rate)
- **Full Time-DP Recompute Latency:** $24.47\text{ ms}$
- **Speedup:** **$6.1\times$ faster** execution while preserving packet delivery under node failure rates up to $30\%$.

---

## Output Figures

Generated plots in `results/`:
- `counterexample_5node.png`: Mechanism isolation diagram of the 5-node counterexample.
- `network_lifetime_comparison.png`: Lifetime curves across all 9 benchmark configurations.
- `network_lifetime_heterogeneous.png`: Dedicated comparison in heterogeneous shadowed environments.
- `sensitivity_time_horizon.png`: Pareto frontier of lookahead horizon $T$ and max hops $H$ vs compute latency.
- `dsu_benchmark_speedup.png`: DSU detour latency speedup and packet recovery curves.
- `energy_heatmap_solar.png`: Residual energy heatmap under diurnal solar harvesting.
- `energy_heatmap_heterogeneous.png`: Residual energy heatmap showing building shadow occlusion.
- `energy_heatmap_stochastic.png`: Residual energy heatmap under Poisson packet arrivals.

---

## Project Structure

```
wsn-energy-routing/
├── src/
│   ├── network.py              # Node and Graph classes, distance and energy tracking
│   ├── energy_model.py         # LEACH first-order radio dissipation model
│   ├── harvesting_model.py     # Solar, Shadowed, RF Hotspot, and Poisson harvesting
│   ├── clustering.py           # LEACH clustering with projected energy
│   ├── routing.py              # Dijkstra, Energy-Aware Dijkstra, A*, and DSU detour
│   ├── dp_lifetime.py          # Classical DP and Time-Augmented DP (dp[v][h][t])
│   ├── simulator.py            # Simulation loop coordinating all phases
│   └── visualize.py            # Matplotlib plotting scripts
├── tests/                      # Pytest unit tests (36 passing tests)
│   ├── test_adversarial_counterexample.py
│   ├── test_energy_aware_dijkstra.py
│   ├── test_heterogeneous_harvesting.py
│   ├── test_dsu_speedup.py
│   └── ...
├── report/
│   └── time_augmented_dp_summary.md  # Detailed algorithm notes, complexity table & proofs
├── run_counterexample.py       # Minimal 5-node adversarial counterexample script
├── run_dsu_benchmark.py        # DSU speedup & packet recovery benchmark
├── run_sensitivity_analysis.py # Horizon (T) and Hop (H) parameter trade-off sweep
├── run_experiments.py          # 9-scenario comparative benchmark suite
├── run_multiseed.py            # Multi-seed (N=5) statistical validation script
├── main.py                     # CLI entrypoint for custom runs
├── pytest.ini                  # Pytest configuration
├── requirements.txt            # Python dependencies
└── README.md                   # Project overview
```

---

## How to Run

### 1. Setup & Tests
```bash
pip install -r requirements.txt
pytest -v
```

### 2. Run Individual Research Experiments
```bash
# 1. 5-Node Minimal Adversarial Counterexample
python run_counterexample.py

# 2. DSU Live Detour Speedup Benchmark
python run_dsu_benchmark.py

# 3. Time Horizon Sensitivity Analysis
python run_sensitivity_analysis.py

# 4. Full 9-Configuration Benchmark Suite
python run_experiments.py

# 5. Multi-Seed Statistical Validation (N=5 seeds)
python run_multiseed.py
```

### 3. Run Custom Simulations via CLI (`main.py`)
```bash
# Standard simulation
python main.py --nodes 50 --rounds 200 --harvesting-profile solar

# Heterogeneous building shadow scenario
python main.py --nodes 50 --rounds 250 --harvesting-profile shadowed

# Compare with Energy-Aware Dijkstra
python main.py --nodes 50 --rounds 200 --routing-algorithm energy_dijkstra --disable-time-dp
```