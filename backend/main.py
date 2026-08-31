"""
FastAPI application for WSN Energy-Harvesting Routing Simulator service.
"""
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
import asyncio
from datetime import datetime

from core.simulator_wrapper import SimulatorWrapper
from db.models import SimulationRun
from db.session import init_db, get_db_session, SessionLocal
from tasks.simulation_tasks import set_job_store, run_simulation_task

app = FastAPI(
    title="WSN Energy-Harvesting Routing Simulator API",
    description="API for running and managing WSN simulations with energy harvesting",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job store for background tasks (simple implementation)
# In production, use Redis, database, or proper task queue like Celery/RQ
jobs: Dict[str, Dict] = {}

# Set the job store in the tasks module
set_job_store(jobs)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

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

@app.post("/simulate", response_model=SimulationResponse)
async def start_simulation(config: SimulationConfig, background_tasks: BackgroundTasks):
    """Start a new simulation run."""
    job_id = str(uuid.uuid4())

    # Store job info
    jobs[job_id] = {
        "status": "pending",
        "config": config.dict(),
        "created_at": datetime.now(),
        "completed_at": None,
        "results": None,
        "error": None
    }

    # Add background task
    background_tasks.add_task(run_simulation_task, job_id, config.dict())

    return SimulationResponse(
        job_id=job_id,
        status="pending",
        message="Simulation started"
    )

@app.get("/simulate/{job_id}/status", response_model=SimulationResultResponse)
async def get_simulation_status(job_id: str):
    """Get the status of a simulation job."""
    if job_id not in jobs:
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
        "created_at": datetime.now(),
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
async def list_runs(limit: int = 10):
    """List recent simulation runs."""
    # Get from database
    db = SessionLocal()
    runs = db.query(SimulationRun).order_by(SimulationRun.created_at.desc()).limit(limit).all()
    db.close()

    return [
        {
            "id": run.id,
            "created_at": run.created_at,
            "parameters": run.parameters,
            "summary": run.summary
        }
        for run in runs
    ]

@app.post("/runs/{run_id}/save")
async def save_simulation_run(run_id: str):
    """Save a completed job to the database."""
    if run_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[run_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")

    # Save to database
    db = SessionLocal()
    db_run = SimulationRun(
        id=int(run_id.split('-')[0], 16) % 1000000,  # Simple hash of UUID for ID
        created_at=job["created_at"],
        parameters=str(job["config"]),  # Store as string (JSON)
        summary=str(job["results"].get("summary", {})) if job["results"] else "{}",
        status=job["status"],
        job_id=run_id
    )
    db.add(db_run)
    db.commit()
    db.refresh(db_run)
    db.close()

    return {"message": "Run saved to database", "id": db_run.id}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "WSN Simulator API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)