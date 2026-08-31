"""
Full test of the API: start a simulation, wait for completion, and check results.
"""
import subprocess
import time
import requests
import json
import sys
import os

def start_server():
    """Start the FastAPI server in the background."""
    os.chdir(os.path.join(os.path.dirname(__file__)))
    server_process = subprocess.Popen(
        [sys.executable, "main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return server_process

def wait_for_server(timeout=10):
    """Wait for the server to be ready."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get("http://localhost:8000/health")
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(0.5)
    return False

def test_full_simulation():
    """Test a full simulation lifecycle."""
    config = {
        "nodes": 10,
        "rounds": 50,
        "area": 50.0,
        "init_energy": 0.5,
        "max_capacity": 1.0,
        "harvesting_profile": "solar",
        "solar_peak": 0.01,
        "seed": 42
    }
    # Start simulation
    response = requests.post("http://localhost:8000/simulate", json=config)
    if response.status_code != 200:
        raise Exception(f"Failed to start simulation: {response.text}")
    data = response.json()
    job_id = data["job_id"]
    print(f"Started simulation with job_id: {job_id}")

    # Poll for completion
    max_attempts = 30
    for i in range(max_attempts):
        time.sleep(2)  # Wait 2 seconds between polls
        status_response = requests.get(f"http://localhost:8000/simulate/{job_id}/status")
        if status_response.status_code != 200:
            raise Exception(f"Failed to get status: {status_response.text}")
        status_data = status_response.json()
        print(f"Attempt {i+1}: status = {status_data['status']}")
        if status_data["status"] == "completed":
            print("Simulation completed!")
            # Check that we have results
            if status_data["results"] is None:
                raise Exception("No results in completed job")
            results = status_data["results"]
            # Validate the results structure
            assert "summary" in results
            assert "time_series" in results
            assert "detailed_data" in results
            summary = results["summary"]
            assert summary["completed_rounds"] == config["rounds"]
            assert summary["final_alive_nodes"] <= config["nodes"]
            assert summary["final_total_energy"] >= 0
            print(f"Results: {json.dumps(summary, indent=2)}")
            return True
        elif status_data["status"] == "failed":
            raise Exception(f"Simulation failed: {status_data.get('error', 'Unknown error')}")
    raise Exception("Simulation did not complete in time")

def main():
    print("Starting server...")
    server = start_server()

    try:
        print("Waiting for server to be ready...")
        if not wait_for_server():
            print("Server did not start in time.")
            server.terminate()
            return False

        print("Server is running. Testing full simulation...")
        success = test_full_simulation()
        if success:
            print("Full simulation test passed!")
        else:
            print("Full simulation test failed.")
        return success

    except Exception as e:
        print(f"Error during testing: {e}")
        return False
    finally:
        # Terminate the server
        print("Terminating server...")
        server.terminate()
        server.wait()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)