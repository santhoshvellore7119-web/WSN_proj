"""
Background tasks for running simulations.
"""
import time
import json
import threading
from datetime import datetime
import os
import sys
from typing import Dict, Any

# Ensure backend directory and project root are in sys.path
_backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)
_root_dir = os.path.abspath(os.path.join(_backend_dir, '..'))
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)

from core.simulator_wrapper import SimulatorWrapper
from db.session import SessionLocal
from db.models import SimulationRun

# Global job store (in-memory fast cache and status tracker)
jobs: Dict[str, Dict] = {}

def set_job_store(job_store: Dict[str, Dict]):
    """Set the job store reference (called from main.py)."""
    global jobs
    jobs = job_store

def run_simulation_task(job_id: str, config: Dict[str, Any]):
    """
    Background task to run a simulation and persist results to SQLite.

    Args:
        job_id: Unique identifier for the job
        config: Simulation configuration dictionary
    """
    # Update job status
    if job_id in jobs:
        jobs[job_id]["status"] = "running"
        jobs[job_id]["started_at"] = time.time()

    try:
        # Create simulator wrapper and run simulation
        wrapper = SimulatorWrapper()

        # Check if this is a benchmark request
        if config.get("benchmark"):
            results = wrapper.run_benchmark()
        else:
            results = wrapper.run_simulation(config)

        # Update in-memory job store
        if job_id in jobs:
            jobs[job_id]["status"] = "completed"
            jobs[job_id]["results"] = results
            jobs[job_id]["completed_at"] = time.time()

        # Auto-persist completed simulation run to SQLite database
        try:
            db = SessionLocal()
            existing = db.query(SimulationRun).filter(SimulationRun.job_id == job_id).first()
            if not existing:
                db_run = SimulationRun(
                    created_at=datetime.utcnow(),
                    parameters=json.dumps(config),
                    summary=json.dumps(results.get("summary", {}) if results else {}),
                    results=json.dumps(results) if results else None,
                    status="completed",
                    job_id=job_id
                )
                db.add(db_run)
                db.commit()
            db.close()
        except Exception as dbe:
            print(f"Warning: Failed to auto-persist run {job_id} to SQLite: {dbe}")

    except Exception as e:
        # Update job with error
        if job_id in jobs:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = str(e)
            jobs[job_id]["completed_at"] = time.time()
        # In production, you'd want to log this error
        print(f"Error in simulation task {job_id}: {e}")