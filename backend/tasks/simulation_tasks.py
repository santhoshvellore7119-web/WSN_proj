"""
Background tasks for running simulations.
"""
import time
import threading
from typing import Dict, Any
from core.simulator_wrapper import SimulatorWrapper

# Global job store (in production, use Redis or database)
# This mirrors the one in main.py for simplicity in this example
jobs: Dict[str, Dict] = {}

def set_job_store(job_store: Dict[str, Dict]):
    """Set the job store reference (called from main.py)."""
    global jobs
    jobs = job_store

def run_simulation_task(job_id: str, config: Dict[str, Any]):
    """
    Background task to run a simulation.

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

        # Update job with results
        if job_id in jobs:
            jobs[job_id]["status"] = "completed"
            jobs[job_id]["results"] = results
            jobs[job_id]["completed_at"] = time.time()

    except Exception as e:
        # Update job with error
        if job_id in jobs:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = str(e)
            jobs[job_id]["completed_at"] = time.time()
        # In production, you'd want to log this error
        print(f"Error in simulation task {job_id}: {e}")