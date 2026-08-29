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

We tested 5 configurations across a 50-node network over 350 rounds (field $100\text{m} \times 100\text{m}$, initial energy $0.045\text{ J}$, battery cap $0.50\text{ J}$, seed 42). Results are fully deterministic — running `run_experiments.py` twice produces identical output.

| Configuration | First Node Death (FND) | Half Nodes Dead (HND) | Alive Nodes (Round 350) | Total Residual Energy |
| :--- | :--- | :--- | :--- | :--- |
| **Baseline (No Harvesting)** | Round 82 | Round 112 | 0 / 50 | 0.0000 J |
| **Solar (Unaware LEACH + Dijkstra)** | Round 165 | Round 209 | 0 / 50 | 0.0000 J |
| **Solar (Adaptive Time-DP)** | Round 165 | Round 208 | 0 / 50 | 0.0000 J |
| **Stochastic Poisson (Unaware LEACH)** | Round 320 | N/A | 40 / 50 | 0.2581 J |
| **Stochastic Poisson (Adaptive Time-DP)** | Round 329 | N/A | **41 / 50** | 0.2532 J |

### Takeaways:
- Solar harvesting (peak rate 0.6 mJ/round, 12-hour day cycle) alone extends first-node-death from round 82 to round 165 — the recharge exactly compensates normal LEACH drain at this parameter setting, so both solar configurations exhaust around the same round.
- Under stochastic Poisson harvesting (λ=2 events/round, 0.15 mJ/event), the cost-aware Time-Augmented DP extends FND from round 320 to round 329 (+2.8%) and keeps one additional node alive at round 350 (41 vs 40), at the cost of slightly lower total residual energy (0.2532 J vs 0.2581 J).
- The slight energy trade-off in the stochastic scenario is expected: the DP distributes relay load across more nodes rather than hammering the same low-cost path, which means more nodes participate in routing — reducing peak depletion but spreading cost more evenly. The network lifetime improvement (more alive nodes, higher FND) is the primary metric.


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
│   ├── time_augmented_dp_summary.md  # Detailed algorithm notes
│   └── first_review_report.md        # Project review report
├── run_experiments.py          # Runs the 5 benchmark comparison scenarios
├── run_simulation.py           # Runs a single sample simulation
├── main.py                     # CLI entrypoint
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
python run_experiments.py
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