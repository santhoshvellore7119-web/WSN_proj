from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import PlainTextResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
import uuid
import json
import asyncio
from datetime import datetime, timezone

import os
import sys

_backend_dir = os.path.abspath(os.path.dirname(__file__))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)
_root_dir = os.path.abspath(os.path.join(_backend_dir, '..'))
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)

from core.simulator_wrapper import SimulatorWrapper
from db.models import SimulationRun
from db.session import init_db, get_db_session, SessionLocal
from tasks.simulation_tasks import set_job_store, run_simulation_task

# Lifespan context manager: initializes SQLite database and cleans up interrupted jobs from previous server runs
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    
    # Auto-recovery: Mark dangling in-flight jobs from prior crashes/restarts as interrupted
    db = SessionLocal()
    try:
        dangling_runs = db.query(SimulationRun).filter(SimulationRun.status.in_(["pending", "running"])).all()
        for run in dangling_runs:
            run.status = "interrupted"
            run.summary = json.dumps({"error": "Server restarted while simulation was in-flight"})
        if dangling_runs:
            db.commit()
    except Exception as e:
        print(f"Warning: Failed to recover dangling runs on startup: {e}")
    finally:
        db.close()

    yield

app = FastAPI(
    title="WSN Energy-Harvesting Routing Simulator API",
    description="Production-grade API for simulating and managing energy-harvesting wireless sensor networks",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS dynamically with environment override (defaulting to local development origins)
cors_env = os.getenv("CORS_ORIGINS", "").strip()
if cors_env == "*":
    allowed_origins = ["*"]
elif cors_env:
    allowed_origins = [origin.strip() for origin in cors_env.split(",") if origin.strip()]
else:
    allowed_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job store for fast polling of running background tasks
jobs: Dict[str, Dict] = {}
set_job_store(jobs)

# Pydantic models with server-side bounds validation
class SimulationConfig(BaseModel):
    nodes: int = Field(50, ge=3, le=500, description="Number of sensor nodes in the network (3 - 500)")
    rounds: int = Field(200, ge=1, le=2000, description="Simulation duration in discrete rounds (1 - 2000)")
    area: float = Field(100.0, ge=10.0, le=1000.0, description="Simulation field dimension in meters (10m - 1000m)")
    init_energy: float = Field(1.0, ge=0.001, le=100.0, description="Initial battery capacity in Joules (0.001J - 100J)")
    max_capacity: float = Field(2.0, ge=0.001, le=100.0, description="Maximum battery capacity in Joules (0.001J - 100J)")
    cluster_ratio: float = Field(0.06, ge=0.01, le=0.5, description="Target cluster head percentage (1% - 50%)")
    bs_x: float = Field(50.0, description="Base station X position coordinate")
    bs_y: float = Field(50.0, description="Base station Y position coordinate")
    harvesting_profile: Optional[str] = Field("solar", description="Harvesting regime: none, constant, solar, stochastic, trace, shadowed_solar")
    solar_peak: float = Field(0.03, ge=0.0, le=10.0, description="Peak solar harvest rate in Joules per round")
    stoch_lambda: float = Field(2.0, ge=0.0, le=100.0, description="Poisson arrival parameter lambda")
    stoch_quantum: float = Field(0.005, ge=0.0, le=10.0, description="Energy per arrival quantum in Joules")
    disable_time_dp: bool = False
    disable_harvesting_ch: bool = False
    disable_live_reroute: bool = False
    max_dp_hops: int = Field(5, ge=1, le=15, description="Maximum multi-hop routing lookahead depth (1 - 15)")
    routing_algorithm: str = Field("dijkstra", description="Routing strategy: dijkstra, energy_dijkstra, astar, dp_maximin, dp_time_augmented")
    seed: Optional[int] = Field(42, description="Pseudorandom generator seed")
    visualize: bool = False

class SimulationResponse(BaseModel):
    job_id: str
    status: str
    message: str

class SimulationResultResponse(BaseModel):
    job_id: str
    status: str
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

class ScalabilityRequest(BaseModel):
    node_counts: Optional[List[int]] = Field([30, 50, 80, 120, 160], description="List of node counts to benchmark")
    rounds: int = Field(150, ge=1, le=1000)
    seed: int = 42

class HeterogeneityRequest(BaseModel):
    shadow_fractions: Optional[List[float]] = Field([0.1, 0.3, 0.5, 0.7, 0.9], description="List of shadow fractions")
    nodes: int = Field(50, ge=10, le=200)
    rounds: int = Field(200, ge=1, le=1000)
    seed: int = 42

@app.post("/simulate", response_model=SimulationResponse)
async def start_simulation(config: SimulationConfig, background_tasks: BackgroundTasks):
    """Start a new simulation run with persistent SQLite tracking."""
    job_id = str(uuid.uuid4())
    cfg_dict = config.model_dump()
    now = datetime.now(timezone.utc)

    # 1. Update in-memory job store
    jobs[job_id] = {
        "status": "pending",
        "config": cfg_dict,
        "created_at": now,
        "completed_at": None,
        "results": None,
        "error": None
    }

    # 2. Persist immediately to SQLite database
    try:
        db = SessionLocal()
        db_run = SimulationRun(
            created_at=now,
            parameters=json.dumps(cfg_dict),
            summary=json.dumps({}),
            results=None,
            status="pending",
            job_id=job_id
        )
        db.add(db_run)
        db.commit()
        db.close()
    except Exception as e:
        print(f"Warning: Failed to create pending record for {job_id} in SQLite: {e}")

    background_tasks.add_task(run_simulation_task, job_id, cfg_dict)

    return SimulationResponse(
        job_id=job_id,
        status="pending",
        message="Simulation started"
    )

@app.get("/simulate/{job_id}/status", response_model=SimulationResultResponse)
async def get_simulation_status(job_id: str):
    """Get the status of a simulation job from in-memory cache or persistent SQLite database."""
    if job_id in jobs:
        job = jobs[job_id]
        return SimulationResultResponse(
            job_id=job_id,
            status=job["status"],
            results=job["results"],
            error=job.get("error"),
            created_at=job["created_at"],
            completed_at=datetime.fromtimestamp(job["completed_at"], tz=timezone.utc) if job.get("completed_at") else None
        )

    # Check SQLite database for completed, failed, or interrupted job
    db = SessionLocal()
    run = db.query(SimulationRun).filter(SimulationRun.job_id == job_id).first()
    db.close()
    if run:
        try:
            res = json.loads(run.results) if run.results else None
        except Exception:
            res = None
        
        err_msg = None
        if run.status in ("failed", "interrupted") and run.summary:
            try:
                summary_data = json.loads(run.summary)
                err_msg = summary_data.get("error")
            except Exception:
                err_msg = run.summary

        return SimulationResultResponse(
            job_id=job_id,
            status=run.status,
            results=res,
            error=err_msg,
            created_at=run.created_at,
            completed_at=run.created_at
        )

    raise HTTPException(status_code=404, detail="Simulation job not found")

def generate_csv_from_results(results: Dict[str, Any]) -> str:
    summary = results.get("summary", {})
    ts = results.get("time_series", {})
    cfg = results.get("configuration", {})
    lines = [
        f"# WSN Energy-Harvesting Simulation Report",
        f"# Algorithm: {cfg.get('routing_algorithm', 'N/A')} | Profile: {cfg.get('harvesting_profile', 'N/A')} | Nodes: {cfg.get('nodes', 'N/A')} | Rounds: {cfg.get('rounds', 'N/A')}",
        f"# FND: {summary.get('first_node_death_round', 'N/A')} | Alive: {summary.get('final_alive_nodes', 'N/A')}/{summary.get('total_nodes', 'N/A')} | Total Residual: {summary.get('final_total_energy', 0):.4f} J",
        f"round,alive_nodes,total_energy_joules,harvested_energy_joules,consumed_energy_joules,reroute_events,jains_fairness_index,packet_delivery_ratio"
    ]
    rounds = ts.get("rounds", [])
    alive = ts.get("alive_nodes", [])
    total_e = ts.get("total_energy", [])
    harv = ts.get("harvested_energy", [])
    cons = ts.get("consumed_energy", [])
    reroutes = ts.get("reroute_events", [])
    fairness = ts.get("fairness_index", [])
    pdr = ts.get("pdr_history", [])
    for i in range(len(rounds)):
        r = rounds[i]
        al = alive[i] if i < len(alive) else 0
        tot = total_e[i] if i < len(total_e) else 0.0
        h = harv[i] if i < len(harv) else 0.0
        c = cons[i] if i < len(cons) else 0.0
        re = reroutes[i] if i < len(reroutes) else 0
        f = fairness[i] if i < len(fairness) else 1.0
        p = pdr[i] if i < len(pdr) else 1.0
        lines.append(f"{r},{al},{tot:.6f},{h:.6f},{c:.6f},{re},{f:.4f},{p:.4f}")
    return "\n".join(lines)

@app.get("/simulate/{job_id}/csv", response_class=PlainTextResponse)
async def get_simulation_csv(job_id: str):
    """Export time-series metrics for a simulation job as downloadable CSV."""
    results_data = None
    if job_id in jobs and jobs[job_id]["results"]:
        results_data = jobs[job_id]["results"]
    else:
        db = SessionLocal()
        run = db.query(SimulationRun).filter(SimulationRun.job_id == job_id).first()
        db.close()
        if run and run.results:
            try:
                results_data = json.loads(run.results)
            except Exception:
                results_data = None
    
    if not results_data or "time_series" not in results_data:
        raise HTTPException(status_code=404, detail="Simulation results not found or still pending")

    csv_text = generate_csv_from_results(results_data)
    return PlainTextResponse(
        content=csv_text,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="wsn_sim_{job_id[:8]}.csv"'}
    )

@app.post("/benchmark")
async def run_benchmark(background_tasks: BackgroundTasks):
    """Run the standard 5-scenario benchmark."""
    job_id = str(uuid.uuid4())

    jobs[job_id] = {
        "status": "pending",
        "config": {"benchmark": True},
        "created_at": datetime.now(timezone.utc),
        "completed_at": None,
        "results": None,
        "error": None
    }

    background_tasks.add_task(run_simulation_task, job_id, {"benchmark": True})

    return SimulationResponse(
        job_id=job_id,
        status="pending",
        message="Benchmark started"
    )

@app.get("/runs")
async def list_runs(limit: int = 25):
    """List recent simulation runs persisted in the SQLite database."""
    db = SessionLocal()
    runs = db.query(SimulationRun).order_by(SimulationRun.created_at.desc()).limit(limit).all()
    db.close()

    out = []
    for run in runs:
        try:
            params = json.loads(run.parameters) if run.parameters and run.parameters.startswith('{') else run.parameters
        except Exception:
            params = run.parameters
        try:
            summary = json.loads(run.summary) if run.summary and run.summary.startswith('{') else run.summary
        except Exception:
            summary = run.summary

        out.append({
            "id": run.id,
            "job_id": run.job_id,
            "created_at": run.created_at.isoformat() if run.created_at else None,
            "parameters": params,
            "summary": summary,
            "status": run.status
        })
    return out

@app.get("/runs/{run_id}")
async def get_run_detail(run_id: str):
    """Get full details and time-series for a specific run from memory or SQLite database."""
    if run_id in jobs and jobs[run_id]["results"]:
        return {
            "job_id": run_id,
            "status": jobs[run_id]["status"],
            "config": jobs[run_id]["config"],
            "summary": jobs[run_id]["results"].get("summary", {}),
            "results": jobs[run_id]["results"]
        }

    db = SessionLocal()
    run = None
    if run_id.isdigit():
        run = db.query(SimulationRun).filter(SimulationRun.id == int(run_id)).first()
    if not run:
        run = db.query(SimulationRun).filter(SimulationRun.job_id == run_id).first()
    db.close()

    if not run:
        raise HTTPException(status_code=404, detail="Run not found in database")

    try:
        params = json.loads(run.parameters) if run.parameters else {}
    except Exception:
        params = run.parameters
    try:
        summary = json.loads(run.summary) if run.summary else {}
    except Exception:
        summary = run.summary
    try:
        results = json.loads(run.results) if run.results else None
    except Exception:
        results = None

    return {
        "id": run.id,
        "job_id": run.job_id,
        "created_at": run.created_at.isoformat() if run.created_at else None,
        "config": params,
        "summary": summary,
        "results": results,
        "status": run.status
    }

@app.post("/runs/{run_id}/save")
async def save_simulation_run(run_id: str):
    """Save a completed job to the SQLite database."""
    if run_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found in active session")

    job = jobs[run_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")

    db = SessionLocal()
    existing = db.query(SimulationRun).filter(SimulationRun.job_id == run_id).first()
    if existing:
        db.close()
        return {"message": "Run already saved in database", "id": existing.id, "job_id": run_id}

    db_run = SimulationRun(
        created_at=job["created_at"] if isinstance(job["created_at"], datetime) else datetime.now(timezone.utc),
        parameters=json.dumps(job["config"]),
        summary=json.dumps(job["results"].get("summary", {}) if job["results"] else {}),
        results=json.dumps(job["results"]) if job["results"] else None,
        status=job["status"],
        job_id=run_id
    )
    db.add(db_run)
    db.commit()
    db.refresh(db_run)
    saved_id = db_run.id
    db.close()

    return {"message": "Run saved to database", "id": saved_id, "job_id": run_id}

@app.delete("/runs/{run_id}")
async def delete_run(run_id: str):
    """Delete a run from the database."""
    db = SessionLocal()
    run = None
    if run_id.isdigit():
        run = db.query(SimulationRun).filter(SimulationRun.id == int(run_id)).first()
    if not run:
        run = db.query(SimulationRun).filter(SimulationRun.job_id == run_id).first()

    if not run:
        db.close()
        raise HTTPException(status_code=404, detail="Run not found")

    db.delete(run)
    db.commit()
    db.close()
    return {"message": "Run deleted", "id": run_id}

@app.post("/experiments/scalability")
async def run_scalability_experiment(req: ScalabilityRequest):
    """Execute scalability benchmarks using core Python Simulator."""
    import time
    from simulator import Simulator
    results = []
    for n in (req.node_counts or [30, 50, 80, 120, 160]):
        sim_base = Simulator(
            num_nodes=n,
            area_width=100.0,
            area_height=100.0,
            seed=req.seed,
            enable_time_dp=False,
            enable_harvesting_ch=False,
            enable_live_reroute=False
        )
        t0 = time.perf_counter()
        sim_base.run(max_rounds=req.rounds, verbose=False)

        sim_adapt = Simulator(
            num_nodes=n,
            area_width=100.0,
            area_height=100.0,
            seed=req.seed,
            enable_time_dp=True,
            enable_harvesting_ch=True,
            enable_live_reroute=True
        )
        sim_adapt.run(max_rounds=req.rounds, verbose=False)
        runtime = (time.perf_counter() - t0) * 1000.0

        results.append({
            "nodes": n,
            "baseline_fnd": sim_base.first_node_death_round,
            "baseline_alive": sim_base.alive_nodes_history[-1] if sim_base.alive_nodes_history else 0,
            "adaptive_fnd": sim_adapt.first_node_death_round,
            "adaptive_alive": sim_adapt.alive_nodes_history[-1] if sim_adapt.alive_nodes_history else 0,
            "computation_ms": round(runtime, 2)
        })
    return results

@app.post("/experiments/heterogeneity")
async def run_heterogeneity_experiment(req: HeterogeneityRequest):
    """Execute spatial heterogeneity sweep using core Python Simulator."""
    from simulator import Simulator
    results = []
    for p in (req.shadow_fractions or [0.1, 0.3, 0.5, 0.7, 0.9]):
        sim_u = Simulator(
            num_nodes=req.nodes,
            seed=req.seed,
            harvesting_profile='heterogeneous_shadowed',
            harvesting_kwargs={'shadow_fraction': p, 'shadow_penalty': 0.1, 'peak_rate': 0.0012},
            enable_time_dp=False,
            enable_harvesting_ch=False,
            enable_live_reroute=False
        )
        sim_u.run(max_rounds=req.rounds, verbose=False)

        sim_dp = Simulator(
            num_nodes=req.nodes,
            seed=req.seed,
            harvesting_profile='heterogeneous_shadowed',
            harvesting_kwargs={'shadow_fraction': p, 'shadow_penalty': 0.1, 'peak_rate': 0.0012},
            enable_time_dp=True,
            enable_harvesting_ch=True,
            enable_live_reroute=True
        )
        sim_dp.run(max_rounds=req.rounds, verbose=False)

        results.append({
            "shadowFraction": p,
            "unaware_fnd": sim_u.first_node_death_round,
            "adaptive_fnd": sim_dp.first_node_death_round,
            "unaware_alive": sim_u.alive_nodes_history[-1] if sim_u.alive_nodes_history else 0,
            "adaptive_alive": sim_dp.alive_nodes_history[-1] if sim_dp.alive_nodes_history else 0,
            "energyRetainedJ": round(sim_dp.total_energy_history[-1] if sim_dp.total_energy_history else 0.0, 4)
        })
    return results

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "WSN Simulator API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)