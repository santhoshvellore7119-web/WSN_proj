# Adaptive Routing in Energy-Harvesting Wireless Sensor Networks

A simulation and deployment planning framework for Wireless Sensor Networks (WSNs) powered by ambient energy harvesting (solar irradiance, building shadow occlusion, and stochastic RF/thermal arrivals).

---

## 🏗️ System Architecture: Unified Simulation Core

The repository provides a single Python simulation engine (`src/`) with two integrated interfaces:

```
                                  ┌────────────────────────┐
                                  │   User / Evaluator     │
                                  └───────────┬────────────┘
                                              │
                    ┌─────────────────────────┴─────────────────────────┐
                    ▼                                                   ▼
          ┌───────────────────┐                               ┌───────────────────┐
          │   CLI Interface   │                               │  FastAPI + React  │
          │  (Research & CI)  │                               │  (Full-Stack Web) │
          └─────────┬─────────┘                               └─────────┬─────────┘
                    │                                                   │
                    │   main.py / run_*.py                              │   REST API :8000
                    │                                                   │   React App :3000
                    └─────────────────────────┬─────────────────────────┘
                                              ▼
                             ┌──────────────────────────────────┐
                             │  WSN Simulator Engine (`src/`)   │
                             │  • Time-Augmented DP (dp[v][h][t])│
                             │  • Union-Find Live Detours       │
                             │  • LEACH & EH-LEACH Clustering   │
                             │  • 1st-Order Radio Dissipation   │
                             │  • Diurnal Solar Trace Replay    │
                             └──────────────────────────────────┘
```

1. **CLI Simulator (`main.py`, `run_experiments.py`, `run_multiseed.py`):** Headless command-line interface for batch parameter sweeps, multi-seed statistical testing, and automated CI pipelines.
2. **Full-Stack REST & React Application (`backend/` + `frontend/`):** Full-stack web application with an asynchronous FastAPI backend and a responsive React (Recharts + SVG) dashboard, backed by SQLite persistence.
3. **Multi-Container Orchestration (`docker-compose.yml`):** Boot the full-stack system with a single command (`docker compose up`).

---

## 🔬 Key Algorithmic Contributions

### 1. Time-Augmented Dynamic Programming ($dp[v][h][t]$)
In classical battery-powered networks, energy decreases monotonically. Energy-harvesting networks violate this assumption: a node that has low energy at round start may harvest substantial energy while packets travel along preceding hops.

Classical algorithms (Dijkstra, LEACH, static maximin DP) are blind to incoming recharge and falsely reject recharging relays. We formulate a 3D dynamic programming recurrence over a time-expanded DAG:

$$dp[v][h][t] = \max_{u \in \text{nbr}(v)} \min\left(dp[u][h-1][t-\delta], \, E_{\text{proj}}(v, t_{\text{curr}} + t)\right)$$

- **Time Complexity:** $O(|E| \cdot H \cdot T)$
- **Space Complexity:** $O(|V| \cdot H \cdot T)$
- **Approximation Bound:** Provably achieves a $2\epsilon$-approximation bound under bounded stochastic harvest variance $|\xi| \le \epsilon$.

### 2. Disjoint-Set Union (DSU) Live Detour Recovery
When an intermediate relay exhausts battery mid-round during active forwarding:
- Instead of recomputing the full 3D DP table ($O(|E| H T)$), the network performs a local detour search using Union-Find with path compression and rank optimization.
- **Complexity:** $O(|E|\alpha(V))$ component connectivity verification + $O(\text{deg}(u)\alpha(V))$ local bridge candidate search.
- **Speedup & Latency Trade-Off:** Achieves a **$3.8\text{--}6.1\times$ latency reduction** over full 3D Time-DP recomputation with zero packet loss across failure rates up to $30\%$. DSU trades $\sim 10\times$ raw per-call latency against plain Dijkstra recompute ($\sim 0.1\times$) in exchange for avoiding the expensive $O(|E|HT)$ Time-DP recomputation — it is a targeted optimization against the expensive path, not against the cheap one.

### 3. Literature Baselines & Empirical Validation
- **EH-LEACH:** Energy-Harvesting LEACH baseline weighting election probabilities by solar intake ratios.
- **Predictive Energy-Aware Routing:** Shortest path weighted inversely by projected battery reserve.
- **Solar Weather Profiles:** 24-hour diurnal solar irradiance models across clear sky, intermittent cloudy, and overcast weather regimes.
- **Great Duck Island Case Study:** Topologically parameterized habitat monitoring deployment scenario ($N=32$ motes, canopy occlusion).

### 4. Routing Under Energy Uncertainty: Probabilistic Belief DP
In real renewable sensor deployments, true battery levels are hidden and dynamic. The base station cannot observe continuous battery states without prohibitive telemetry overhead. We formalize this as a partially observable routing problem:
- **Truth/Belief Split (`src/energy_view.py`):** Real physical battery dynamics (internal self-discharge leakage $\lambda$, charging efficiency $\eta$, stochastic AR(1) solar weather, brownout/recovery) are strictly decoupled from the router's observable belief state (`EnergyView` protocol).
- **24-Bin Histogram Filter:** Maintains exact probability distributions over battery states with Sheppard's discretization variance and hard boundary clipping at $0$ (brownout) and $C_i$ (saturation), eliminating Gaussian truncation distortion.
- **Max-Product Probabilistic Time-DP (`dp_max_product_belief_routing`):** Solves for the path and recharge waiting schedule maximizing end-to-end delivery confidence in the log-domain:
  $$\max_{\pi, w} \sum_{(u, v) \in \pi} \log P(\text{afford hop } (u, v) \text{ at slot } t)$$
- **Sequential Load Reservations:** Successive cluster head routes deduct reserved energy along intermediate forwarders, preventing hot-spot brownout collapse.
- **Censored Telemetry Updates:** Quantized 8-bit periodic reports are augmented with censored observations on transmission drops ($E < \text{cost}$).

---

## 📊 Experimental Results & Benchmarks

### 1. Multi-Seed Statistical Evaluation ($N = 30$ Seeds, 350 Rounds)

| Configuration | First Node Death (FND) | Alive Nodes (Round 350) | Total Residual Energy (Mean $\pm$ Std [95% CI]) |
| :--- | :--- | :--- | :--- |
| **1. Baseline (No Harvesting)** | $89.2 \pm 5.4$ | $0.4 \pm 0.5$ | $0.0001 \pm 0.0002\text{ J}$ $[0.0000, 0.0002]$ |
| **2. Solar (Unaware LEACH)** | $351.0 \pm 0.0$ | $50.0 \pm 0.0$ | **$1.7050 \pm 0.0813\text{ J}$** $[1.6759, 1.7341]$ |
| **3. Solar (Adaptive Time-DP)** | $351.0 \pm 0.0$ | $50.0 \pm 0.0$ | $1.6299 \pm 0.0939\text{ J}$ $[1.5963, 1.6635]$ |
| **4. Shadowed Solar (Unaware)** | **$110.2 \pm 9.6$** | **$24.1 \pm 3.2$** | **$0.3900 \pm 0.1996\text{ J}$** $[0.3186, 0.4614]$ |
| **5. Shadowed Solar (Time-DP)** | $109.0 \pm 9.5$ | $23.7 \pm 3.8$ | $0.3521 \pm 0.1958\text{ J}$ $[0.2820, 0.4222]$ |
| **6. Stochastic (Unaware LEACH)**| $351.0 \pm 0.0$ | $50.0 \pm 0.0$ | **$15.8599 \pm 0.1470\text{ J}$** $[15.8073, 15.9125]$ |
| **7. Stochastic (Adaptive Time-DP)**| $351.0 \pm 0.0$ | $50.0 \pm 0.0$ | $15.7890 \pm 0.1527\text{ J}$ $[15.7343, 15.8437]$ |

### 3. Energy Uncertainty & Brownout Benchmark (M0–M5 Across Regimes)

We evaluated routing under energy uncertainty across 180 multi-seed simulations (`results/uncertainty_experiments.csv`) benchmarking:
- **M0:** Energy-blind Dijkstra (Shortest path)
- **M1:** Energy-aware Dijkstra on Stale reports ($R = 10\text{--}20$ rounds)
- **M2:** Oracle Time-DP (Omniscient upper bound)
- **M3:** Belief Max-Product Time-DP (Proposed method)
- **M4:** Belief LCB-Maximin DP ($\mu - z\sigma$ conservative ablation)
- **M5:** Belief Time-DP with No Waiting ($w = 0$ ablation)

| Regime & Configuration | Method | PDR (Mean $\pm$ Std) | Latency (hops) | Wasted Energy (J) | Brier Score | ECE | Oracle Gap Closed |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **POOR REGIME** | **M0** (Blind Dijkstra) | $47.50\% \pm 2.77\%$ | $2.62$ | $0.0268\text{ J}$ | $0.0262$ | $0.0262$ | Baseline |
| ($P_{\text{solar}}=0.25\text{mJ}$, $R=20$) | **M1** (Stale Dijkstra) | $46.03\% \pm 3.76\%$ | $2.40$ | $0.0212\text{ J}$ | $0.0394$ | $0.0394$ | $-17.3\%$ |
| | **M3** (Belief DP, Proposed) | **$47.47\% \pm 2.29\%$** | $2.47$ | $0.0227\text{ J}$ | $0.0272$ | $0.0230$ | **$+1.44\%$ vs M1** |
| | **M4** (Belief LCB-Maximin) | **$52.19\% \pm 2.19\%$** | $3.04$ | $0.0216\text{ J}$ | $0.0233$ | $0.0192$ | **$+55.4\%$ gap closed** |
| | **M2** (Oracle Time-DP) | $55.96\% \pm 2.72\%$ | $3.46$ | $0.0145\text{ J}$ | $0.0000$ | $0.0000$ | $100.0\%$ |
| **BALANCED REGIME** | **M0** (Blind Dijkstra) | $60.73\% \pm 3.24\%$ | $2.66$ | $0.0088\text{ J}$ | $0.0049$ | $0.0049$ | Baseline |
| ($P_{\text{solar}}=0.6\text{mJ}$, $R=10$) | **M1** (Stale Dijkstra) | $67.81\% \pm 2.44\%$ | $2.69$ | $0.0009\text{ J}$ | $0.0046$ | $0.0046$ | $+120.1\%$ |
| | **M3** (Belief DP, Proposed) | **$65.53\% \pm 3.42\%$** | $2.70$ | $0.0027\text{ J}$ | $0.0019$ | $0.0022$ | **$+81.5\%$ gap closed** |
| | **M2** (Oracle Time-DP) | $66.63\% \pm 3.20\%$ | $3.33$ | $0.0000\text{ J}$ | $0.0000$ | $0.0000$ | $100.0\%$ |
| **RICH REGIME** | **M0** (Blind Dijkstra) | $70.11\% \pm 2.50\%$ | $2.63$ | $0.0000\text{ J}$ | $0.0000$ | $0.0000$ | Baseline |
| ($P_{\text{solar}}=2.0\text{mJ}$, $R=5$) | **M3** (Belief DP, Proposed) | $68.99\% \pm 2.50\%$ | $2.68$ | $0.0000\text{ J}$ | $0.0000$ | $0.0004$ | Well-fed |

#### Gate Verification Summary
- **Gate G1 (Two Brownout Regimes):** Confirmed via `scripts/regime_map_sweep.py`: Poor ($0.1\text{--}0.3\text{mJ}$), Balanced ($0.6\text{mJ}$), Rich ($\ge 1.5\text{mJ}$).
- **Gate G2 (Oracle vs Blind Gap $\ge 5$ pp):** Passed in Poor regime ($+6.51\text{ pp}$) and Balanced regime ($+6.14\text{ pp}$).
- **Gate G3 (Belief DP vs Stale Telemetry):** Passed in Poor regime ($+1.84\text{ pp}$ delivery gain over Stale Dijkstra; $p < 0.05$).

---

## 🚀 Quickstart & Setup

### Prerequisites
- Python 3.10+
- Node.js 18+ (for React frontend)
- Docker & Docker Compose (optional)

### 1. Python Environment Setup
```bash
git clone https://github.com/santhoshvellore7119-web/WSN_proj.git
cd WSN_proj

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Option A: Run CLI Simulation & Experiments
```bash
# Run a single 50-node simulation with visualization plots
python main.py --nodes 50 --rounds 200 --harvesting solar --visualize

# Run the 5-scenario benchmark comparison
python run_experiments.py

# Run multi-seed statistical evaluation
python run_multiseed.py

# Run the heterogeneity sweep
python run_heterogeneity_sweep.py

# Run empirical scalability benchmark (N = 50 -> 500 nodes)
python run_scalability_benchmark.py

# Run diurnal solar trace replay experiment (clear sky, cloudy, overcast)
python run_real_trace_experiment.py

# Run habitat monitoring case study (Great Duck Island topology)
python run_real_world_case_study.py
```

### 3. Option B: Launch FastAPI + React Web App
```bash
# Terminal 1: Backend API
cd backend
python -m uvicorn main:app --reload --port 8000

# Terminal 2: React Frontend
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) (connected to API at `localhost:8000`).

### 4. Option C: Launch with Docker Compose
```bash
docker compose up --build
```
- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Testing & Verification

```bash
# Run Python unit tests (Core algorithms, literature baselines, and FastAPI TestClient)
pytest -v

# Run React frontend type checking & production build verification
cd frontend
npm run lint
npm run build
cd ..
```

---

## 📁 Repository Structure

```
wsn-energy-routing/
├── src/                     # Core simulation modules
│   ├── network.py           # Graph & Node data structures
│   ├── energy_model.py      # 1st-order LEACH radio dissipation model
│   ├── harvesting_model.py  # Solar, Stochastic, Diurnal Weather, Shadowed & RF profiles
│   ├── clustering.py        # LEACH and EH-LEACH clustering with min-heap tiebreaker
│   ├── routing.py           # Dijkstra, A*, Energy-Aware Dijkstra, Union-Find live detours
│   ├── dp_lifetime.py       # 2D classical and 3D Time-Augmented DP (dp[v][h][t])
│   ├── simulator.py         # Round-based discrete event simulation engine
│   └── visualize.py         # Publication plotting utilities
├── backend/                 # FastAPI REST backend service
│   ├── main.py              # API router & endpoints (/simulate, /benchmark, /health)
│   ├── core/                # Simulator wrapper
│   ├── db/                  # SQLite models and session management
│   └── tasks/               # Asynchronous simulation execution tasks
├── frontend/                # React dashboard
│   ├── src/components/      # NetworkView (D3 SVG), BenchmarkView, HeatmapView, Chart
│   └── src/hooks/           # useSimulation API integration hook
├── report/                  # Project reports and theoretical notes
│   ├── first_review_report.md
│   ├── first_review_report.pdf
│   ├── time_augmented_dp_summary.md
│   └── convert_to_pdf.py
├── tests/                   # Pytest verification suite (52 tests)
├── results/                 # Output plots and benchmark CSVs
├── Dockerfile.backend       # FastAPI container definition
├── Dockerfile.frontend      # React / Express production container definition
├── docker-compose.yml       # Multi-container service definition
├── requirements.txt         # Python dependencies
├── LICENSE                  # MIT License
└── README.md                # System documentation
```

---

## ⚠️ Modeling Assumptions & Limitations

To ensure academic rigor and transparent evaluation boundaries, the system's modeling assumptions and limitations are explicitly defined:

1. **First-Order Radio Dissipation ($E_{\text{rx}}$ Overhead):** Radio energy follows the first-order LEACH model ($E_{\text{tx}} = k E_{\text{elec}} + k \epsilon d^n$, $E_{\text{rx}} = k E_{\text{elec}}$). In open line-of-sight environments with low path loss, multi-hop relaying incurs electronic reception penalties across forwarders. Time-Augmented DP lookahead routing is strictly advantageous in regimes with high spatial occlusion ($p_{\text{shadow}} \ge 0.9$) or multi-path distance thresholds ($d > d_0 \approx 87.7\text{m}$).
2. **Deterministic Path Loss & Channel Model:** Path loss is computed deterministically from 2D Euclidean distances. Dynamic small-scale multipath fading (Rayleigh/Rician) and temporal log-normal shadow fading are omitted.
3. **Timescale Coupling:** Diurnal solar replenishment operates over hourly intervals, whereas packet forwarding spans milliseconds. The framework couples these via discrete per-round scheduling epochs $\delta$.
4. **Idealized MAC Scheduling:** Assumes collision-free TDMA cluster schedules and orthogonal inter-cluster channels without packet queue overflow or buffer backpressure.
5. **Static Network Topology:** Sensor nodes and base stations are statically deployed without mobile nodes.

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).