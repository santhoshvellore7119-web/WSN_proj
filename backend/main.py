"""
FastAPI application for WSN Energy-Harvesting Routing Simulator service.
"""
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
import uuid
import json
import asyncio
from datetime import datetime

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

# Lifespan context manager replacing deprecated @app.on_event
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="WSN Energy-Harvesting Routing Simulator API",
    description="API for running and managing WSN simulations with energy harvesting",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS with explicit local development origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job store for fast polling of running background tasks
jobs: Dict[str, Dict] = {}
set_job_store(jobs)

# Pydantic models for request/response
class SimulationConfig(BaseModel):
    nodes: int = 50
    rounds: int = 200
    area: float = 100.0
    init_energy: float = 1.0
    max_capacity: float = 2.0
    cluster_ratio: float = 0.06
    bs_x: float = 50.0
    bs_y: float = 50.0
    harvesting_profile: Optional[str] = "solar"
    solar_peak: float = 0.03
    stoch_lambda: float = 2.0
    stoch_quantum: float = 0.005
    disable_time_dp: bool = False
    disable_harvesting_ch: bool = False
    disable_live_reroute: bool = False
    max_dp_hops: int = 5
    routing_algorithm: str = "dijkstra"
    seed: Optional[int] = 42
    visualize: bool = True

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
    node_counts: Optional[List[int]] = [30, 50, 80, 120, 160]
    rounds: int = 150
    seed: int = 42

class HeterogeneityRequest(BaseModel):
    shadow_fractions: Optional[List[float]] = [0.1, 0.3, 0.5, 0.7, 0.9]
    nodes: int = 50
    rounds: int = 200
    seed: int = 42

@app.post("/simulate", response_model=SimulationResponse)
async def start_simulation(config: SimulationConfig, background_tasks: BackgroundTasks):
    """Start a new simulation run."""
    job_id = str(uuid.uuid4())
    cfg_dict = config.model_dump()

    jobs[job_id] = {
        "status": "pending",
        "config": cfg_dict,
        "created_at": datetime.utcnow(),
        "completed_at": None,
        "results": None,
        "error": None
    }

    background_tasks.add_task(run_simulation_task, job_id, cfg_dict)

    return SimulationResponse(
        job_id=job_id,
        status="pending",
        message="Simulation started"
    )

@app.get("/simulate/{job_id}/status", response_model=SimulationResultResponse)
async def get_simulation_status(job_id: str):
    """Get the status of a simulation job."""
    if job_id not in jobs:
        # Check SQLite database for completed job
        db = SessionLocal()
        run = db.query(SimulationRun).filter(SimulationRun.job_id == job_id).first()
        db.close()
        if run:
            try:
                res = json.loads(run.results) if run.results else None
            except Exception:
                res = None
            return SimulationResultResponse(
                job_id=job_id,
                status=run.status,
                results=res,
                error=None,
                created_at=run.created_at,
                completed_at=run.created_at
            )
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    return SimulationResultResponse(
        job_id=job_id,
        status=job["status"],
        results=job["results"],
        error=job["error"],
        created_at=job["created_at"],
        completed_at=job["completed_at"]
    )

@app.post("/benchmark")
async def run_benchmark(background_tasks: BackgroundTasks):
    """Run the standard 5-scenario benchmark."""
    job_id = str(uuid.uuid4())

    jobs[job_id] = {
        "status": "pending",
        "config": {"benchmark": True},
        "created_at": datetime.utcnow(),
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
        created_at=job["created_at"] if isinstance(job["created_at"], datetime) else datetime.utcnow(),
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