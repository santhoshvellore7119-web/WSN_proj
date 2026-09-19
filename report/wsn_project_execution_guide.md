# WSN Energy-Harvesting Routing Simulator
## Full-Stack Web Application Execution & Setup Guide (FastAPI Backend + React Frontend)

**GitHub Repository:** [https://github.com/santhoshvellore7119-web/WSN_proj](https://github.com/santhoshvellore7119-web/WSN_proj)  
**Branch:** `master` &nbsp;|&nbsp; **Author:** Santhosh &nbsp;|&nbsp; **Date:** September 2026

---

## 1. Full-Stack System Architecture Overview

The project consists of a complete full-stack web application integrating an asynchronous Python FastAPI backend with an interactive React 19 single-page dashboard:

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

| Layer | Tech Stack & Port | Role & Responsibilities |
| :--- | :--- | :--- |
| **Frontend UI** | React 19, TypeScript, Vite, Tailwind CSS, Recharts<br/>**Port 3000** | Interactive single-page application. Features real-time SVG sensor topology canvas, round-by-round replay controls, and dynamic residual energy line charts. |
| **Backend API** | FastAPI, Uvicorn, SQLite, SQLAlchemy, Pydantic<br/>**Port 8000** | Asynchronous REST API. Manages background simulation jobs, SQLite database persistence (`backend/wsn_simulator.db`), and provides OpenAPI / Swagger documentation. |
| **Simulation Engine** | Python 3.10+, NumPy, SciPy<br/>(Core Library in `src/`) | Executes 3D Time-Augmented DP ($dp[v][h][t]$), DSU live detour recovery, LEACH clustering, 1st-order radio model, and solar harvesting profiles. |

---

> [!CAUTION]
> **CRITICAL WORKING DIRECTORY REQUIREMENT:**
> - **Project Root:** `C:\Users\Santhosh\wsn-energy-routing`
> - **Frontend Directory:** `C:\Users\Santhosh\wsn-energy-routing\frontend`
> - **DO NOT** execute commands inside `C:\Users\Santhosh\frontend` (which is an unrelated, separate project).
> - Executing commands in the wrong directory will trigger `npm error Missing script: "dev"` or `Could not open requirements file: 'requirements.txt'`.

---

## 2. Prerequisites & One-Time Initial Setup

Ensure the following tools are installed on your machine:
- **Python 3.10+** (with `pip`)
- **Node.js 18+** (with `npm`)
- **Git**

### Step 1: Open or Clone the Repository
```cmd
cd C:\Users\Santhosh\wsn-energy-routing
```
*(If cloning on a new machine: `git clone https://github.com/santhoshvellore7119-web/WSN_proj.git wsn-energy-routing && cd wsn-energy-routing`)*

### Step 2: Setup Python Virtual Environment & Install Backend Dependencies
- **Windows (CMD / PowerShell):**
  ```cmd
  cd C:\Users\Santhosh\wsn-energy-routing
  python -m venv .venv
  .venv\Scripts\activate
  python -m pip install --upgrade pip
  pip install -r requirements.txt
  ```
  *(Note: Always use `python -m pip install` to avoid Windows file-locking update errors).*

- **Linux / macOS:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  python3 -m pip install --upgrade pip
  pip install -r requirements.txt
  ```

### Step 3: Install Frontend Node Dependencies
```cmd
cd C:\Users\Santhosh\wsn-energy-routing\frontend
npm install
cd ..
```

---

## 3. How to Run the Full-Stack Application

### Method A: Automated 1-Click Startup (Recommended)
A pre-configured startup batch script is included in the project root to automatically manage ports, activate environments, and launch both servers:
```cmd
cd C:\Users\Santhosh\wsn-energy-routing
.\start_offline.bat
```
*(Or simply double-click `start_offline.bat` in Windows File Explorer. It cleans busy ports 8000/3000, starts FastAPI, starts React, and opens http://localhost:3000 in your browser).*

### Method B: Manual Startup in Two Terminals
To run both the backend API and frontend UI manually, open **two separate terminal windows**:

#### Terminal 1: Start the FastAPI Backend (Port 8000)
```cmd
cd C:\Users\Santhosh\wsn-energy-routing
.venv\Scripts\activate
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
- **Backend API URL:** `http://127.0.0.1:8000`
- **Interactive Swagger Docs:** `http://127.0.0.1:8000/docs`
- **Redoc Documentation:** `http://127.0.0.1:8000/redoc`

#### Terminal 2: Start the React Frontend (Port 3000)
```cmd
cd C:\Users\Santhosh\wsn-energy-routing\frontend
npm run dev
```
- **Frontend Dashboard URL:** `http://localhost:3000`
- **Automatic Proxying:** `frontend/server.ts` automatically forwards all `/api/*` requests to the FastAPI backend at `http://127.0.0.1:8000`.

---

## 4. Step-by-Step Procedure to Run in Visual Studio Code (VS Code)

### Step 1: Open Project in VS Code
Launch VS Code at the project root:
```bash
cd C:\Users\Santhosh\wsn-energy-routing
code .
```

### Step 2: Select Python Interpreter
1. Press `Ctrl + Shift + P` (or `Cmd + Shift + P` on macOS).
2. Type and select **Python: Select Interpreter**.
3. Choose the workspace virtual environment: `.\.venv\Scripts\python.exe` (or `./.venv/bin/python`).

### Step 3: Open Integrated Split Terminals
1. Open the integrated terminal with ``Ctrl + ` ``.
2. Click the **Split Terminal** button on the top right of the terminal panel (or press `Ctrl + \`).
3. In the **Left Pane (Backend)**, run:
   ```cmd
   .\.venv\Scripts\activate
   python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
   ```
4. In the **Right Pane (Frontend)**, run:
   ```cmd
   cd frontend
   npm run dev
   ```

### Step 4: Optional 1-Click Debugging via `.vscode/launch.json`
Add to `.vscode/launch.json` for 1-click breakpoint debugging:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug FastAPI Backend",
      "type": "debugpy",
      "request": "launch",
      "module": "uvicorn",
      "args": ["backend.main:app", "--reload", "--port", "8000"],
      "jinja": true
    }
  ]
}
```

---

## 5. Running with Docker Compose (1-Command Full-Stack Boot)

If you have Docker Desktop installed, boot both containers simultaneously without configuring local environments:

```bash
# Build and start all services in detached mode
docker compose up --build -d

# View live logs from both services
docker compose logs -f

# Stop and clean up containers
docker compose down
```

- **Web Dashboard:** [http://localhost:3000](http://localhost:3000)
- **FastAPI Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 6. Key REST API Endpoints Overview

| Method & Route | Request Body / Params | Functionality |
| :--- | :--- | :--- |
| `POST /api/run-simulation` | JSON: `{ num_nodes, rounds, harvesting_profile, enable_time_dp, ... }` | Triggers asynchronous simulation in background task. Returns job ID. |
| `GET /api/simulation/{id}` | Path param: `job_id` (UUID) | Polls live execution status, node topology coordinates, and round telemetry. |
| `GET /api/scenarios` | None | Returns pre-configured scenario templates (Baseline, Solar, Shadowed, Stochastic). |
| `GET /api/history` | Query: `limit`, `offset` | Retrieves paginated past simulation runs stored in SQLite. |
| `GET /api/export/{id}/csv` | Path param: `job_id` | Exports round-by-round energy, alive nodes, and packet metrics as CSV. |

---

## 7. Troubleshooting & Common Issues

| Symptom / Error | Underlying Cause | Resolution |
| :--- | :--- | :--- |
| **`npm error Missing script: "dev"`** | Command was run in `C:\Users\Santhosh\frontend` (unrelated Create-React-App project) instead of the actual project frontend folder. | Navigate to `cd C:\Users\Santhosh\wsn-energy-routing\frontend` and verify `package.json` contains `"dev": "tsx server.ts"`. |
| **`ERROR: Could not open requirements file: 'requirements.txt'`** | Terminal is inside `frontend\` or outside the project root. `requirements.txt` is in the root directory. | Run `cd C:\Users\Santhosh\wsn-energy-routing` before executing `pip install -r requirements.txt`. |
| **`ERROR: To modify pip, please run python.exe -m pip...`** | Windows binary-locking prevents `pip.exe` from modifying its own file in-place during upgrade. | Always run the module invocation: `python -m pip install --upgrade pip`. |
| **`PowerShell execution policy blocks activate.ps1`** | Default Windows PowerShell policy blocks local script execution. | Run once in PowerShell: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`. |
| **`Port 8000 or 3000 already in use`** | Previous server processes were left running in the background. | Run `start_offline.bat` (auto-cleans ports) or run: `netstat -ano \| findstr :8000` and `taskkill /PID <PID> /F`. |
| **`502 Bad Gateway / Network Error in Browser`** | Frontend proxy cannot connect to backend because FastAPI is offline. | Ensure FastAPI backend is running on port 8000 before accessing the frontend on port 3000. |

---

## 8. Quick Full-Stack Execution Cheat-Sheet

```cmd
# -------------------------------------------------------------
# OPTION A: ONE-CLICK LAUNCH (FASTEST)
# -------------------------------------------------------------
cd C:\Users\Santhosh\wsn-energy-routing
.\start_offline.bat

# -------------------------------------------------------------
# OPTION B: MANUAL TWO-TERMINAL SETUP
# -------------------------------------------------------------
# Terminal 1 (FastAPI Backend - Port 8000):
cd C:\Users\Santhosh\wsn-energy-routing
.venv\Scripts\activate
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

# Terminal 2 (React Frontend - Port 3000):
cd C:\Users\Santhosh\wsn-energy-routing\frontend
npm run dev

# Access in Browser:
# Dashboard: http://localhost:3000  |  API Docs: http://127.0.0.1:8000/docs
```
