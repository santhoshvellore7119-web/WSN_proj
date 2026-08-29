# WSN Energy-Harvesting Routing Simulator

A 2nd-year B.Tech Data Structures & Algorithms course project exploring adaptive routing in Wireless Sensor Networks (WSNs) with energy harvesting.

---

## About the Project

In standard sensor networks, nodes run on non-rechargeable batteries, so residual energy only goes down over time. Protocols like LEACH or Dijkstra make sense here because once a node is low on battery, you should avoid routing traffic through it.

However, when nodes are equipped with energy harvesters (like small solar panels or ambient RF collectors), their battery level is no longer monotonic—a node with low energy right now might recharge in a few time steps. If we only look at instantaneous battery levels, we end up ignoring nodes that would be perfectly good relays by the time a packet actually arrives.

This project implements a round-based WSN simulator in Python to study how routing and clustering can take advantage of incoming harvested energy.

### What We Implemented:
1. **Time-Augmented Maximin DP (`dp[v][h][t]`):** An extension of bottleneck dynamic programming that includes a discrete time dimension $t$. Instead of only checking static energy at round start, it projects future recharge so packets can route through nodes that recharge just-in-time.
2. **Harvesting-Aware LEACH Clustering:** Modifies the standard LEACH cluster head election threshold to account for expected energy harvest over the round.
3. **Union-Find (DSU) Live Rerouting:** Uses a Disjoint-Set Union structure with path compression and rank optimization to quickly find a local detour if an intermediate relay node runs out of power mid-round, avoiding a full route recalculation.
4. **Harvesting Models:** Implements diurnal day/night solar cycles and stochastic Poisson energy arrivals with battery capacity caps.

---

## How It Works

During each simulation round:
1. **Harvesting:** Nodes collect energy according to their harvesting profile (solar periodic or Poisson arrivals) up to their battery capacity.
2. **Cluster Head Election:** Nodes run a modified LEACH election where probability is scaled by projected energy. Member nodes join the nearest elected cluster head.
3. **Routing to Base Station:** Cluster heads find paths to the base station using either shortest path (Dijkstra) or Time-Augmented DP.
4. **Data Transmission:** Packets are forwarded along the chosen paths. If an intermediate node unexpectedly runs out of energy, the DSU module finds an immediate local detour to an alternate neighbor connected to the base station.
5. **Energy Accounting:** Transmission ($E_{tx}$) and reception ($E_{rx}$) energy costs are deducted using the first-order radio model ($d^2$ free-space / $d^4$ multipath).

---

## The Time-Augmented DP Algorithm

### Why classical DP is not enough
Standard bottleneck DP tracks $(v, h)$—the maximum bottleneck residual energy to reach node $v$ in $h$ hops:
$$\text{dp}[v][h] = \max_{u \in \text{nbr}(v)} \min\left(\text{dp}[u][h-1], \, E_v(t_0)\right)$$

If node $v$ has $0.05\text{ J}$ at $t_0$, classical DP rejects it. But if the packet takes 2 hops to reach $v$, and $v$ harvests $+0.8\text{ J}$ in those 2 steps, its real energy at arrival is $0.85\text{ J}$. 

### Our 3D DP Formulation
We add a discrete time offset $t$:
$$\text{dp}[v][h][t] = \text{max bottleneck energy to reach node } v \text{ in } h \text{ hops at arrival offset } t$$

**Projected Energy:**
$$E_{\text{proj}}(v, t_{\text{curr}} + t) = \min\left(E_{\max}(v), \, E_v(t_{\text{curr}}) + \text{ExpectedHarvest}(v, t_{\text{curr}} \to t_{\text{curr}} + t)\right)$$

**Recurrence:**
For sensor nodes:
$$\text{dp}[v][h][t] = \max_{u \in \text{nbr}(v)} \left\{ \min\left(\text{dp}[u][h-1][t - \delta], \, E_{\text{proj}}(v, t_{\text{curr}} + t)\right) \right\}$$

For the Base Station (node $-1$):
$$\text{dp}[-1][h][t] = \max_{u \in \text{nbr}(-1)} \left\{ \text{dp}[u][h-1][t - \delta] \right\}$$

We reconstruct the path and arrival timeline by following predecessor pointers stored during the DP table fill.

---

## Experimental Results

### 1. Canonical Single-Seed Benchmark (Seed 42)
Tested across a 50-node network over 350 rounds (field $100\text{m} \times 100\text{m}$, initial energy $0.045\text{ J}$, battery cap $0.50\text{ J}$):

| Configuration | First Node Death (FND) | Half Nodes Dead (HND) | Alive Nodes (Round 350) | Total Residual Energy |
| :--- | :--- | :--- | :--- | :--- |
| **Baseline (No Harvesting)** | Round 82 | Round 112 | 0 / 50 | 0.0000 J |
| **Solar (Unaware LEACH + Dijkstra)** | Round 165 | Round 209 | 0 / 50 | 0.0000 J |
| **Solar (Adaptive Time-DP)** | Round 165 | Round 208 | 0 / 50 | 0.0000 J |
| **Stochastic Poisson (Unaware LEACH)** | Round 320 | N/A | 40 / 50 | 0.2581 J |
| **Stochastic Poisson (Adaptive Time-DP)** | Round 329 | N/A | **41 / 50** | 0.2532 J |

---

### 2. Multi-Seed Statistical Validation ($N = 5$ Independent Topologies)
To verify that results are not an artefact of a single lucky topology, we evaluated all 5 configurations across 5 independent random seeds (`[42, 7, 123, 256, 999]`):

| Configuration | FND ($\mu \pm \sigma$) | HND ($\mu \pm \sigma$) | Alive Nodes ($\mu \pm \sigma$) | Residual Energy ($\mu \pm \sigma$) |
| :--- | :--- | :--- | :--- | :--- |
| **Baseline (No Harvesting)** | $83.0 \pm 3.9$ | $110.2 \pm 1.3$ | $0.0 \pm 0.0$ | $0.0000 \pm 0.0000\text{ J}$ |
| **Solar (Unaware LEACH + Dijkstra)** | $160.6 \pm 3.6$ | $207.0 \pm 4.7$ | $0.2 \pm 0.4$ | $0.0036 \pm 0.0080\text{ J}$ |
| **Solar (Adaptive Time-DP)** | $159.6 \pm 4.9$ | $207.0 \pm 4.7$ | $0.2 \pm 0.4$ | $0.0036 \pm 0.0080\text{ J}$ |
| **Stochastic Poisson (Unaware LEACH)** | $280.2 \pm 32.4$ | $> 350$ | $38.8 \pm 3.3$ | $0.1998 \pm 0.0596\text{ J}$ |
| **Stochastic Poisson (Adaptive Time-DP)** | $280.0 \pm 43.3$ | $> 350$ | $37.8 \pm 4.0$ | $0.2004 \pm 0.0616\text{ J}$ |

---

### 3. Critical Analysis & Academic Takeaways
- **Spatial Topology Variance vs. Algorithmic Effect**: Across 5 random seeds, node placement variance ($\sigma \approx 32\text{--}43\text{ rounds}$) is large because cluster-head distance to the sink varies per deployment. 
- **Synchronous Solar Invariance**: Under uniform diurnal solar cycles, ambient recharge is spatially homogeneous. Because all nodes experience daylight and darkness simultaneously, the relative energy gradient between neighbors remains flat, causing energy-aware paths and shortest paths to converge.
- **Cost-Aware Tie-Breaking Necessity**: Standard maximin DP optimizes solely for bottleneck capacity, occasionally picking circuitous paths. Our 1% relative tolerance tie-breaker ensures that physically cheaper paths (lower transmission and reception energy) win when bottlenecks are comparable, eliminating wasteful routing detours.
- **When Time-Augmented DP is Essential**: Time-DP provides significant advantage in heterogeneous/asynchronous recharge regimes (e.g. localized solar occlusion, RF burst harvesting, or spatial traffic hotspots) where future energy projections actively differentiate viable relays from rapidly depleting ones.


---

## Output Figures

Generated plots are saved in the `results/` folder:
- `network_lifetime_comparison.png`: Comparison curves of alive nodes and residual energy over rounds.
- `energy_heatmap_solar.png`: 2D heatmap showing per-node energy levels through day/night solar cycles.
- `energy_heatmap_stochastic.png`: Heatmap under stochastic Poisson energy arrivals.
- `routing_tree_round_*.png`: Network topology showing sensor positions, elected cluster heads, and routing paths to the base station.

---

## Project Structure

```
wsn-energy-routing/
├── src/
│   ├── network.py              # Node and Graph classes, distance and energy tracking
│   ├── energy_model.py         # LEACH first-order radio dissipation model
│   ├── harvesting_model.py     # Solar, Poisson, and constant harvesting profiles
│   ├── clustering.py           # LEACH clustering with projected energy
│   ├── routing.py              # Dijkstra, A*, Union-Find, and DSU live detour rerouting
│   ├── dp_lifetime.py          # Classical DP and Time-Augmented DP (dp[v][h][t])
│   ├── simulator.py            # Simulation loop coordinating all phases
│   └── visualize.py            # Matplotlib plotting scripts
├── tests/                      # Pytest unit tests (31 tests)
├── results/                    # Saved plots and CSV output logs
├── report/
│   └── time_augmented_dp_summary.md  # Detailed algorithm notes & recurrence proofs
├── run_experiments.py          # Runs the 5 benchmark comparison scenarios
├── run_multiseed.py            # Multi-seed (N=5) statistical validation script
├── main.py                     # CLI entrypoint for custom runs and benchmarks
├── requirements.txt            # Python dependencies
└── README.md                   # Project overview
```

---

## How to Run

### 1. Setup
```bash
git clone https://github.com/santhoshvellore7119-web/WSN_proj.git
cd WSN_proj
pip install -r requirements.txt
```

### 2. Run Tests
```bash
pytest -v
```

### 3. Run a Simulation
```bash
# Run default simulation (50 nodes, 200 rounds, solar harvesting)
python main.py

# Custom run with CLI flags
python main.py --nodes 60 --rounds 150 --harvesting-profile solar --solar-peak 0.04
```

### 4. Run the Full Comparison Suite
```bash
# Single-seed canonical benchmark and plot generation
python run_experiments.py

# Multi-seed statistical validation (N=5 independent random seeds)
python run_multiseed.py
```

---

## CLI Options (`main.py`)

- `--nodes`: Number of sensor nodes (default: 50)
- `--rounds`: Maximum simulation rounds (default: 200)
- `--area`: Field size in meters (default: 100.0)
- `--init-energy`: Starting energy per node in Joules (default: 1.0)
- `--max-capacity`: Maximum battery capacity in Joules (default: 2.0)
- `--harvesting-profile`: `none`, `constant`, `solar`, or `stochastic` (default: `solar`)
- `--solar-peak`: Peak recharge rate for solar model (default: 0.03)
- `--stoch-lambda`: Poisson arrival rate (default: 2.0)
- `--disable-time-dp`: Flag to use standard Dijkstra instead of Time-DP
- `--disable-harvesting-ch`: Flag to disable harvest weighting in LEACH
- `--disable-live-reroute`: Flag to disable DSU detour recovery
- `--benchmark`: Runs all 5 comparison scenarios directly