# Adaptive Routing in Energy-Harvesting Wireless Sensor Networks
## System Architecture, Mathematical Foundation, and Full-Stack Execution Manual

**GitHub Repository:** [https://github.com/santhoshvellore7119-web/WSN_proj](https://github.com/santhoshvellore7119-web/WSN_proj)  
**Branch:** `master` &nbsp;|&nbsp; **Author:** Santhosh &nbsp;|&nbsp; **Date:** September 2026

---

## 1. Project Overview & Problem Formulation

In classical battery-powered Wireless Sensor Networks (WSNs), sensor node battery levels decrease monotonically. Consequently, standard routing protocols (Dijkstra, LEACH, static maximin Dynamic Programming) evaluate nodes using static battery snapshots.

In Energy-Harvesting WSNs (EH-WSNs), nodes recharge dynamically from ambient sources (solar, RF, thermal). Static routing algorithms suffer from two critical failure modes:
1. **False Rejection of Recharging Relays:** Relays with low battery at round start are discarded, even though they will harvest sufficient energy *just-in-time* while data packets traverse preceding hops.
2. **Premature Partitioning of Shaded Relays:** Non-harvesting shaded nodes are over-utilized along shortest paths, causing premature node death and network disconnection.

This project delivers a unified simulation engine, algorithmic innovations, and a modern full-stack web application for research and deployment planning.

### System Architecture Overview

| Subsystem | Technology Stack | Key Capabilities & Role |
| :--- | :--- | :--- |
| **Simulation Core** | Python 3.10+, NumPy, SciPy, Matplotlib | 3D Time-Augmented DP, DSU detour repair, 1st-order radio model, LEACH/EH-LEACH, diurnal solar traces, 52 unit tests. |
| **Backend API** | FastAPI, Uvicorn, SQLite, Pydantic, SQLAlchemy | Async REST API (Port 8000), background job execution, simulation persistence, interactive Swagger/OpenAPI docs. |
| **Frontend UI** | React 19, TypeScript, Vite, Tailwind CSS, Recharts | Interactive SPA (Port 3000), live node topology canvas, round-by-round replay, multi-metric time-series analytics. |
| **Containerization** | Docker, Docker Compose | Multi-service container orchestration bundling backend and frontend for zero-configuration deployment. |

---

## 2. Key Algorithmic Contributions & Physical Modeling

- **3D Time-Augmented Dynamic Programming ($dp[v][h][t]$):**
  $$dp[v][h][t] = \max_{u \in \text{nbr}(v)} \min\left(dp[u][h-1][t-\delta], \, E_{\text{proj}}(v, t_{\text{curr}} + t)\right)$$
  Operates in polynomial time $O(|E| \cdot H \cdot T)$ and space $O(|V| \cdot H \cdot T)$ (<50 kB RAM), providing provable $2\epsilon$-approximation bounds under bounded stochastic harvest variance $|\xi| \le \epsilon$.
- **Disjoint-Set Union (DSU) Live Detour Recovery:** Slices local alternate paths around depleted intermediate relays in $O(|E|\alpha(V) + \text{deg}(u)\alpha(V))$, maintaining 0% packet loss and achieving a **$3.3\text{--}6.1\times$ speedup** over global Time-DP recalculation.
- **First-Order Radio Dissipation & Reception Penalty ($E_{\text{rx}}$):** Models physical transmission dissipation $E_{\text{tx}} = k \cdot (E_{\text{elec}} + \epsilon_{\text{fs}} \cdot d^2)$ (or $\epsilon_{\text{mp}} \cdot d^4$) alongside unavoidable electronic reception dissipation $E_{\text{rx}} = k \cdot E_{\text{elec}}$ on all intermediate forwarders.
- **Diurnal Solar & Shadow Trace Replay:** Evaluates 24-hour diurnal solar irradiance profiles (clear sky, intermittent cloudy, overcast) and canopy occlusion fractions ($p_{\text{shadow}} \in [0.0, 1.0]$).

---

## 3. Prerequisites & Environment Setup

### Required Software
- **Python:** Version 3.10 or higher (tested on Python 3.12)
- **Node.js:** Version 18+ and `npm` (for the React frontend)
- **Git:** For cloning and version control
- **Docker & Docker Compose:** *(Optional)* for containerized deployment

### Step 1: Clone Repository
```bash
git clone https://github.com/santhoshvellore7119-web/WSN_proj.git
cd WSN_proj
```

### Step 2: Create & Activate Virtual Environment
- **Windows (Command Prompt / PowerShell):**
  ```cmd
  python -m venv .venv
  .venv\Scripts\activate
  ```
- **Linux / macOS:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### Step 3: Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Verify Installation (Pytest Suite)
```bash
pytest -q
```
*Expected output: `52 passed in < 3.5s`*

---

## 4. Running CLI Simulations & Experiments in CMD / PowerShell

All simulation scenarios, multi-seed statistical tests, and benchmark sweeps can be executed directly from Command Prompt or PowerShell:

| Script / Command | Description & Output Artifacts |
| :--- | :--- |
| `python main.py --nodes 50 --rounds 200 --harvesting solar --visualize` | Runs a single 50-node simulation with interactive Matplotlib topology and energy history plots. |
| `python run_experiments.py` | Executes the 5 canonical scenarios (Baseline, Solar Unaware, Solar Time-DP, Shadowed, Stochastic). Outputs comparison charts in `results/`. |
| `python run_multiseed.py` | Runs 30-seed Monte Carlo evaluation (350 rounds/seed). Computes paired t-tests, Wilcoxon W, Cohen's d, and 95% Confidence Intervals. |
| `python run_heterogeneity_sweep.py` | Sweeps canopy occlusion $p_{\text{shadow}} \in [0.0, 1.0]$. Generates sensitivity curves demonstrating the multi-hop $E_{\text{rx}}$ reception threshold. |
| `python run_scalability_benchmark.py` | Measures empirical latency scaling from $N=50$ to $N=500$ nodes with isolated timer blocks (Dijkstra vs DP vs Time-DP vs DSU Detour). |
| `python run_dsu_benchmark.py` | Benchmarks DSU detour repair speedup across failure rates (0%–30%) over 10 seeds, showing $3.3\text{--}6.1\times$ speedup over Time-DP recomputation. |
| `python run_real_trace_experiment.py` | Replays 24-hour diurnal solar irradiance profiles across Clear Sky, Cloudy, and Overcast conditions. |
| `python run_real_world_case_study.py` | Runs the Great Duck Island habitat monitoring case study ($N=32$ motes with spatial canopy heterogeneity). |

---

## 5. Step-by-Step Setup & Execution in VS Code

### 1. Open Workspace
Launch VS Code in the project root:
```bash
code .
```

### 2. Select Python Interpreter
1. Press `Ctrl + Shift + P` (or `Cmd + Shift + P` on macOS).
2. Type and select `Python: Select Interpreter`.
3. Choose the virtual environment interpreter: `.\.venv\Scripts\python.exe` (or `./.venv/bin/python`).

### 3. Setup Split Terminals for Full-Stack Development
1. Open the integrated terminal (`Ctrl + ~`).
2. Click the **Split Terminal** icon (`Ctrl + \`).
3. **Pane 1 (FastAPI Backend):**
   ```bash
   cd backend
   python -m uvicorn main:app --reload --port 8000
   ```
4. **Pane 2 (React Frontend):**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### 4. VS Code Debugging (`.vscode/launch.json`)
Create or edit `.vscode/launch.json` for 1-click debugging with breakpoints:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI Backend",
      "type": "debugpy",
      "request": "launch",
      "module": "uvicorn",
      "args": ["backend.main:app", "--reload", "--port", "8000"],
      "jinja": true
    },
    {
      "name": "Python: Run Experiments",
      "type": "debugpy",
      "request": "launch",
      "program": "${workspaceFolder}/run_experiments.py"
    }
  ]
}
```

---

## 6. Full-Stack Web Application Development Workflow

The full-stack application connects a modern React 19 single-page application to an asynchronous FastAPI Python backend:

```
┌─────────────────────────────────┐        HTTP / API Proxy       ┌─────────────────────────────────┐
│     React Frontend (Vite)       │ ────────────────────────────> │       FastAPI Backend API       │
│     http://localhost:3000       │ <──────────────────────────── │      http://localhost:8000      │
└─────────────────────────────────┘                               └────────────────┬────────────────┘
                                                                                   │
                                                                   ┌───────────────┴────────────────┐
                                                                   ▼                                ▼
                                                     ┌───────────────────────────┐    ┌───────────────────────────┐
                                                     │  SQLite Database Storage  │    │  WSN Simulator Core Engine│
                                                     │  (wsn_simulator.db)       │    │  (Time-DP, DSU, Clustering│
                                                     └───────────────────────────┘    └───────────────────────────┘
```

### Starting the Backend
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```
- **API Base:** `http://localhost:8000`
- **Interactive Swagger Docs:** `http://localhost:8000/docs`
- **Redoc Documentation:** `http://localhost:8000/redoc`

### Starting the Frontend
```bash
cd frontend
npm install
npm run dev
```
- **Web App Dashboard:** `http://localhost:3000`
- The Vite server (`server.ts`) automatically forwards all `/api/*` calls to `http://127.0.0.1:8000`.

### Key Backend REST API Endpoints

| HTTP Method & Route | Request Body / Params | Function & Description |
| :--- | :--- | :--- |
| `POST /api/run-simulation` | JSON config payload (`num_nodes`, `rounds`, `harvesting_profile`, `enable_time_dp`, ...) | Launches asynchronous simulation task in background. |
| `GET /api/simulation/{job_id}` | Path param: `job_id` (UUID) | Returns live status, node spatial coordinates, and round-by-round energy telemetry. |
| `GET /api/scenarios` | None | Returns list of pre-configured scenario templates. |
| `GET /api/history` | Query: `limit`, `offset` | Fetches historical simulation runs from SQLite database. |
| `GET /api/export/{job_id}/csv` | Path param: `job_id` | Downloads complete per-round metrics as a CSV spreadsheet. |

---

## 7. Containerized Deployment via Docker Compose

To boot both backend and frontend in isolated containers with a single command:

```bash
# Build and launch all services in detached mode
docker compose up --build -d

# View live container logs
docker compose logs -f

# Stop and remove containers
docker compose down
```

- **Frontend Dashboard:** [http://localhost:3000](http://localhost:3000)
- **FastAPI Backend Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 8. Troubleshooting & Common Pitfalls

1. **PowerShell Script Execution Disabled:**
   - *Error:* `running scripts is disabled on this system`
   - *Fix:* Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in PowerShell, then reactivate `.venv\Scripts\activate`.
2. **Port 8000 or 3000 Already in Use:**
   - *Error:* `[Errno 10048] address already in use`
   - *Fix (Windows):* `netstat -ano | findstr :8000` then `taskkill /PID <PID> /F`.
   - *Fix (Linux/macOS):* `lsof -ti:8000 | xargs kill -9`.
3. **ModuleNotFoundError: No module named 'src':**
   - *Fix:* Always execute Python experiment scripts from the repository root directory.
4. **502 Bad Gateway / Backend Service Unavailable on Frontend:**
   - *Fix:* Ensure the FastAPI backend is running on `localhost:8000` before launching the frontend dev server.

---

## 9. Quick Command Reference Cheat-Sheet

```bash
# Setup
git clone https://github.com/santhoshvellore7119-web/WSN_proj.git
cd WSN_proj
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
pytest -q

# Full-Stack Development
# Terminal 1 (Backend):
cd backend && python -m uvicorn main:app --reload --port 8000

# Terminal 2 (Frontend):
cd frontend && npm install && npm run dev

# Docker (One-Command Boot):
docker compose up --build
```
