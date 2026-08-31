"""
Test the benchmark endpoint.
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

def test_benchmark():
    """Test the benchmark endpoint."""
    # Start benchmark
    response = requests.post("http://localhost:8000/benchmark")
    if response.status_code != 200:
        raise Exception(f"Failed to start benchmark: {response.text}")
    data = response.json()
    job_id = data["job_id"]
    print(f"Started benchmark with job_id: {job_id}")

    # Poll for completion
    max_attempts = 30
    for i in range(max_attempts):
        time.sleep(3)  # Wait 3 seconds between polls (benchmark might take longer)
        status_response = requests.get(f"http://localhost:8000/simulate/{job_id}/status")
        if status_response.status_code != 200:
            raise Exception(f"Failed to get status: {status_response.text}")
        status_data = status_response.json()
        print(f"Attempt {i+1}: status = {status_data['status']}")
        if status_data["status"] == "completed":
            print("Benchmark completed!")
            # Check that we have results
            if status_data["results"] is None:
                raise Exception("No results in completed benchmark job")
            results = status_data["results"]
            # The benchmark results are expected to have a 'benchmark_output' field
            assert "benchmark_output" in results
            output = results["benchmark_output"]
            assert isinstance(output, str)
            assert len(output) > 0
            print(f"Benchmark output length: {len(output)} characters")
            # Optionally, we can check for expected strings in the output
            assert "Baseline (No Harvest)" in output
            assert "Solar (Unaware LEACH)" in output
            assert "Solar (Adaptive Time-DP)" in output
            assert "Stochastic (Unaware LEACH)" in output
            assert "Stochastic (Adaptive Time-DP)" in output
            print("Benchmark output contains expected scenario names.")
            return True
        elif status_data["status"] == "failed":
            raise Exception(f"Benchmark failed: {status_data.get('error', 'Unknown error')}")
    raise Exception("Benchmark did not complete in time")

def main():
    print("Starting server...")
    server = start_server()

    try:
        print("Waiting for server to be ready...")
        if not wait_for_server():
            print("Server did not start in time.")
            server.terminate()
            return False

        print("Server is running. Testing benchmark...")
        success = test_benchmark()
        if success:
            print("Benchmark test passed!")
        else:
            print("Benchmark test failed.")
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