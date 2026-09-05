"""
Unit tests for FastAPI backend routes using TestClient.
"""

import sys
import os
import json
from datetime import datetime, timezone
from fastapi.testclient import TestClient

# Add project root and backend path (do not add src at top level before fastapi initializes)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
backend_path = os.path.join(PROJECT_ROOT, 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from backend.main import app

client = TestClient(app)


def test_health_check():
    """Verify /health endpoint returns healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "WSN Simulator API"}


from unittest.mock import patch

def test_simulate_endpoint():
    """Verify /simulate endpoint accepts config and creates pending job."""
    with patch("backend.main.run_simulation_task") as mock_task:
        payload = {
            "nodes": 10,
            "rounds": 10,
            "area": 50.0,
            "init_energy": 0.5,
            "max_capacity": 1.0,
            "cluster_ratio": 0.1,
            "harvesting_profile": "solar",
            "solar_peak": 0.01,
            "seed": 42,
            "visualize": False
        }
        response = client.post("/simulate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "pending"

        # Check status endpoint for this job
        job_id = data["job_id"]
        status_resp = client.get(f"/simulate/{job_id}/status")
        assert status_resp.status_code == 200
        status_data = status_resp.json()
        assert status_data["job_id"] == job_id


def test_benchmark_endpoint():
    """Verify /benchmark endpoint starts a benchmark task."""
    with patch("backend.main.run_simulation_task") as mock_task:
        response = client.post("/benchmark")
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "pending"


def test_invalid_job_status():
    """Verify non-existent job ID returns 404."""
    response = client.get("/simulate/non-existent-uuid/status")
    assert response.status_code == 404


def test_runs_endpoint():
    """Verify /runs list endpoint returns JSON list."""
    response = client.get("/runs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_scalability_experiment_endpoint():
    """Verify /experiments/scalability executes Python simulation benchmarks."""
    payload = {
        "node_counts": [10, 20],
        "rounds": 10,
        "seed": 42
    }
    response = client.post("/experiments/scalability", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert "baseline_fnd" in data[0]
    assert "adaptive_fnd" in data[0]
    assert "computation_ms" in data[0]


def test_heterogeneity_experiment_endpoint():
    """Verify /experiments/heterogeneity executes spatial heterogeneity sweep."""
    payload = {
        "shadow_fractions": [0.2, 0.5],
        "nodes": 20,
        "rounds": 15,
        "seed": 42
    }
    response = client.post("/experiments/heterogeneity", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert "shadowFraction" in data[0]
    assert "unaware_fnd" in data[0]
    assert "adaptive_fnd" in data[0]
    assert "energyRetainedJ" in data[0]


def test_csv_export_endpoint():
    """Verify /simulate/{job_id}/csv generates CSV for completed simulation."""
    from backend.main import jobs
    mock_id = "test-job-csv-123"
    jobs[mock_id] = {
        "status": "completed",
        "config": {"routing_algorithm": "dp_time_augmented", "harvesting_profile": "solar", "nodes": 10, "rounds": 5},
        "results": {
            "summary": {"first_node_death_round": None, "final_alive_nodes": 10, "total_nodes": 10, "final_total_energy": 5.2},
            "configuration": {"routing_algorithm": "dp_time_augmented", "harvesting_profile": "solar", "nodes": 10, "rounds": 5},
            "time_series": {
                "rounds": [1, 2, 3, 4, 5],
                "alive_nodes": [10, 10, 10, 10, 10],
                "total_energy": [5.0, 5.1, 5.2, 5.3, 5.2],
                "harvested_energy": [0.1, 0.1, 0.1, 0.1, 0.1],
                "consumed_energy": [0.05, 0.05, 0.05, 0.05, 0.05],
                "reroute_events": [0, 0, 0, 0, 0],
                "fairness_index": [1.0, 1.0, 1.0, 1.0, 1.0],
                "pdr_history": [1.0, 1.0, 1.0, 1.0, 1.0]
            }
        },
        "created_at": None,
        "completed_at": None,
        "error": None
    }
    resp = client.get(f"/simulate/{mock_id}/csv")
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["content-type"]
    assert "round,alive_nodes,total_energy_joules" in resp.text
    assert "1,10,5.000000" in resp.text


def test_simulation_validation_bounds_rejection():
    """Verify that out-of-bounds parameters are rejected with HTTP 422."""
    # Test excessive node count
    invalid_nodes_payload = {"nodes": 10000, "rounds": 100}
    resp = client.post("/simulate", json=invalid_nodes_payload)
    assert resp.status_code == 422
    err_detail = resp.json()["detail"]
    assert any("nodes" in str(err["loc"]) for err in err_detail)

    # Test negative rounds
    invalid_rounds_payload = {"nodes": 50, "rounds": -10}
    resp = client.post("/simulate", json=invalid_rounds_payload)
    assert resp.status_code == 422

    # Test excessive max_dp_hops
    invalid_hops_payload = {"nodes": 50, "rounds": 100, "max_dp_hops": 99}
    resp = client.post("/simulate", json=invalid_hops_payload)
    assert resp.status_code == 422


def test_job_status_sqlite_fallback_and_recovery():
    """Verify that jobs stored in SQLite can be queried even if memory cache is cleared."""
    import uuid
    from backend.db.session import SessionLocal
    from backend.db.models import SimulationRun
    from backend.main import jobs, lifespan
    import asyncio

    job_id = f"test-sql-recovery-{uuid.uuid4().hex[:8]}"
    
    # Insert dangling 'running' simulation directly in DB
    db = SessionLocal()
    try:
        run = SimulationRun(
            job_id=job_id,
            status="running",
            parameters=json.dumps({"nodes": 20, "rounds": 50}),
            created_at=datetime.now(timezone.utc)
        )
        db.add(run)
        db.commit()
    finally:
        db.close()

    # Ensure memory dict does not contain it
    if job_id in jobs:
        del jobs[job_id]

    # Status check should read from SQLite and return "running"
    resp = client.get(f"/simulate/{job_id}/status")
    assert resp.status_code == 200
    assert resp.json()["status"] == "running"

    # Test startup lifespan recovery marks it as "interrupted"
    async def run_lifespan():
        async with lifespan(app):
            pass
    asyncio.run(run_lifespan())

    # Check updated status from SQLite
    resp = client.get(f"/simulate/{job_id}/status")
    assert resp.status_code == 200
    assert resp.json()["status"] == "interrupted"


