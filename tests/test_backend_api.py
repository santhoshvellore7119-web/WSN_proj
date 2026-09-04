"""
Unit tests for FastAPI backend routes using TestClient.
"""

import sys
import os
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

