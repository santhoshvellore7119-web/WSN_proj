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
                             │  • Real-Trace Solar Replay (NREL)│
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
- **Complexity:** $O(\text{deg}(u) \cdot \alpha(V))$
- **Speedup:** Achieves a **$6.1\times$ latency reduction** over full table recalculation with zero packet loss across failure rates up to $30\%$.

### 3. Literature Baselines & Empirical Validation
- **EH-LEACH:** Energy-Harvesting LEACH baseline weighting election probabilities by solar intake ratios.
- **Predictive Energy-Aware Routing:** Shortest path weighted inversely by projected battery reserve.
- **Real Solar Trace Replay:** Integrated empirical 24-hour solar irradiance traces calibrated from NREL NSRDB data across clear, cloudy, and overcast profiles.

---

## 📊 Experimental Results & Benchmarks

### 1. Multi-Seed Statistical Evaluation ($N = 30$ Seeds, 350 Rounds)

| Configuration | First Node Death (FND) | Alive Nodes (Round 350) | Total Residual Energy |
| :--- | :--- | :--- | :--- |
| **1. Baseline (No Harvesting)** | $89.2 \pm 5.4$ | $0.4 \pm 0.5$ | $0.0001 \pm 0.0002\text{ J}$ |
| **2. Solar (Unaware LEACH)** | $351.0 \pm 0.0$ | $50.0 \pm 0.0$ | **$1.7050 \pm 0.0813\text{ J}$** |
| **3. Solar (Adaptive Time-DP)** | $351.0 \pm 0.0$ | $50.0 \pm 0.0$ | $1.6299 \pm 0.0939\text{ J}$ |
| **4. Shadowed Solar (Unaware)** | **$110.2 \pm 9.6$** | **$24.1 \pm 3.2$** | **$0.3900 \pm 0.1996\text{ J}$** |
| **5. Shadowed Solar (Time-DP)** | $109.0 \pm 9.5$ | $23.7 \pm 3.8$ | $0.3521 \pm 0.1958\text{ J}$ |
| **6. Stochastic (Unaware LEACH)**| $351.0 \pm 0.0$ | $50.0 \pm 0.0$ | **$15.8599 \pm 0.1470\text{ J}$** |
| **7. Stochastic (Adaptive Time-DP)**| $351.0 \pm 0.0$ | $50.0 \pm 0.0$ | $15.7890 \pm 0.1527\text{ J}$ |

### 2. Theoretical vs. Network-Level Trade-Offs
- **Single-Path Maximin Optimality (Theorem 1):** Proves Bellman optimality on time-expanded DAGs for worst-case bottleneck capacity, isolating recharging relays on targeted paths (5-node counterexample).
- **The Relay Dissipation Trade-Off ($E_{\text{rx}}$):** In dense uncoordinated networks, multi-hop routing incurs reception energy dissipation ($E_{\text{rx}} = k \cdot E_{\text{elec}}$) on intermediate relays. Shortest-path Dijkstra preserves more aggregate network energy unless extreme spatial occlusion ($p_{\text{shadow}} = 1.0$) forces lookahead detour routing (+6 rounds FND).

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

# Run real solar trace replay (NREL data)
python run_real_trace_experiment.py
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
│   ├── harvesting_model.py  # Solar, Stochastic, Real-Trace (NREL), Shadowed & RF profiles
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
├── tests/                   # Pytest verification suite (46 tests)
├── results/                 # Output plots and benchmark CSVs
├── Dockerfile.backend       # FastAPI container definition
├── Dockerfile.frontend      # React / Nginx container definition
├── docker-compose.yml       # Multi-container service definition
├── requirements.txt         # Python dependencies
├── LICENSE                  # MIT License
└── README.md                # System documentation
```

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).