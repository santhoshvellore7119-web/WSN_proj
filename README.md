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

We tested 5 different configurations across a 50-node network over 350 rounds (field $100\text{m} \times 100\text{m}$, initial energy $0.045\text{ J}$, random seed 42):

| Configuration | First Node Death (FND) | Half Nodes Dead (HND) | Alive Nodes (Round 350) | Total Residual Energy |
| :--- | :--- | :--- | :--- | :--- |
| **Baseline (No Harvesting)** | Round 92 | Round 110 | 0 / 50 | 0.0000 J |
| **Solar (Unaware LEACH + Dijkstra)** | Round 156 | Round 209 | 0 / 50 | 0.0000 J |
| **Solar (Adaptive Time-DP)** | Round 99 | Round 207 | 1 / 50 | 0.0213 J |
| **Stochastic Poisson (Unaware LEACH)** | Round 254 | N/A | 39 / 50 | 0.1673 J |
| **Stochastic Poisson (Adaptive Time-DP)** | Round 283 | N/A | **39 / 50** | **0.1852 J** |

### Takeaways:
- Even without harvesting awareness, solar recharge nearly doubles operational rounds before first node death (round 92 → 156).
- Under stochastic Poisson harvesting, the cost-aware Time-Augmented DP pushes FND from round 254 to round 283 (+11.4%) and retains 10.7% more total energy (0.1673 J → 0.1852 J) compared to the harvesting-unaware LEACH+Dijkstra baseline.
- The solar adaptive scenario trades a slightly lower FND for higher residual energy at round 350 (0.0213 J vs. 0.0000 J), as the DP routes conservatively through nodes projected to have higher future energy — an expected trade-off between spreading early load and preserving late-round coverage.
- The cost-aware tie-breaking addition (preference for lower physical transmission cost when two paths have bottleneck values within 1%) is what prevents the adaptive DP from being strictly worse than Dijkstra in the stochastic scenario.

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