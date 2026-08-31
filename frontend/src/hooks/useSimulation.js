import { useState, useCallback } from 'react';

const API_BASE_URL = 'http://localhost:8000';

export const useSimulation = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);
  const [jobId, setJobId] = useState(null);

  const runSimulation = useCallback(async (config) => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      // Start simulation
      const response = await fetch(`${API_BASE_URL}/simulate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
      });

      if (!response.ok) {
        throw new Error(`Failed to start simulation: ${response.statusText}`);
      }

      const data = await response.json();
      setJobId(data.job_id);

      // Poll for completion
      while (true) {
        await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second

        const statusResponse = await fetch(`${API_BASE_URL}/simulate/${data.job_id}/status`);
        if (!statusResponse.ok) {
          throw new Error(`Failed to get status: ${statusResponse.statusText}`);
        }

        const statusData = await statusResponse.json();

        if (statusData.status === 'completed') {
          setResults(statusData.results);
          setLoading(false);
          break;
        } else if (statusData.status === 'failed') {
          setError(statusData.error || 'Simulation failed');
          setLoading(false);
          break;
        }
        // Still pending/running, continue polling
      }
    } catch (err) {
      setError(err.message);
      setLoading(false);
      throw err;
    }
  }, []);

  const runBenchmark = useCallback(async () => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      // Start benchmark
      const response = await fetch(`${API_BASE_URL}/benchmark`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error(`Failed to start benchmark: ${response.statusText}`);
      }

      const data = await response.json();
      setJobId(data.job_id);

      // Poll for completion
      while (true) {
        await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2 seconds for benchmark

        const statusResponse = await fetch(`${API_BASE_URL}/simulate/${data.job_id}/status`);
        if (!statusResponse.ok) {
          throw new Error(`Failed to get status: ${statusResponse.statusText}`);
        }

        const statusData = await statusResponse.json();

        if (statusData.status === 'completed') {
          setResults(statusData.results);
          setLoading(false);
          break;
        } else if (statusData.status === 'failed') {
          setError(statusData.error || 'Benchmark failed');
          setLoading(false);
          break;
        }
        // Still pending/running, continue polling
      }
    } catch (err) {
      setError(err.message);
      setLoading(false);
      throw err;
    }
  }, []);

  const reset = useCallback(() => {
    setLoading(false);
    setError(null);
    setResults(null);
    setJobId(null);
  }, []);

  return {
    runSimulation,
    runBenchmark,
    loading,
    error,
    results,
    jobId,
    reset
  };
};