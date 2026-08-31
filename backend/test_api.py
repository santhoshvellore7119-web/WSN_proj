"""
Test script to run the backend API and test the endpoints.
"""
import subprocess
import time
import requests
import json
import sys
import os

def start_server():
    """Start the FastAPI server in the background."""
    # Change to the backend directory
    os.chdir(os.path.join(os.path.dirname(__file__)))
    # Start the server
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

def test_simulate_endpoint():
    """Test the /simulate endpoint."""
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
    response = requests.post("http://localhost:8000/simulate", json=config)
    return response.json()

def test_benchmark_endpoint():
    """Test the /benchmark endpoint."""
    response = requests.post("http://localhost:8000/benchmark")
    return response.json()

def main():
    print("Starting server...")
    server = start_server()

    try:
        print("Waiting for server to be ready...")
        if not wait_for_server():
            print("Server did not start in time.")
            server.terminate()
            return False

        print("Server is running. Testing endpoints...")

        # Test health endpoint
        health_response = requests.get("http://localhost:8000/health")
        print(f"Health check: {health_response.json()}")

        # Test simulate endpoint
        simulate_result = test_simulate_endpoint()
        print(f"Simulate endpoint response: {json.dumps(simulate_result, indent=2)}")

        # Test benchmark endpoint (optional, as it may take longer)
        # benchmark_result = test_benchmark_endpoint()
        # print(f"Benchmark endpoint response: {json.dumps(benchmark_result, indent=2)}")

        print("Tests completed successfully.")
        return True

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