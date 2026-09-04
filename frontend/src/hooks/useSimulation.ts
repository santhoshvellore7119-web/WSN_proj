import { useState, useCallback } from 'react';
import { SimulationConfig, SimulationResults, BenchmarkResults } from '../types';

export function useSimulation() {
  const [loading, setLoading] = useState<boolean>(false);
  const [progressText, setProgressText] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<SimulationResults | null>(null);
  const [benchmarkResults, setBenchmarkResults] = useState<BenchmarkResults | null>(null);
  const [benchmarkLoading, setBenchmarkLoading] = useState<boolean>(false);
  const [jobId, setJobId] = useState<string | null>(null);

  const runSimulation = useCallback(async (config: SimulationConfig) => {
    setLoading(true);
    setError(null);
    setProgressText('Submitting simulation to Python backend...');

    try {
      const res = await fetch('/api/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || `Backend returned status ${res.status}`);
      }

      const data = await res.json();
      setJobId(data.job_id);
      setProgressText('Simulating rounds in Python engine...');

      // Poll backend job status until completed
      let attempts = 0;
      const maxAttempts = 240; // 60s timeout
      while (attempts < maxAttempts) {
        await new Promise(r => setTimeout(r, 300));
        const statusRes = await fetch(`/api/simulate/${data.job_id}/status`);
        if (statusRes.ok) {
          const statusData = await statusRes.json();
          if (statusData.status === 'completed' && statusData.results) {
            setResults(statusData.results);
            setLoading(false);
            setProgressText('');
            return;
          } else if (statusData.status === 'failed') {
            throw new Error(statusData.error || 'Backend simulation failed');
          }
        }
        attempts++;
      }
      throw new Error('Simulation timed out waiting for backend response');
    } catch (err: any) {
      console.error('Simulation error:', err);
      setError(err?.message || 'Simulation encountered an error. Ensure the FastAPI backend is running on port 8000.');
      setLoading(false);
      setProgressText('');
    }
  }, []);

  const runBenchmark = useCallback(async (nodes: number = 50, rounds: number = 300, seed: number = 42) => {
    setBenchmarkLoading(true);
    setError(null);
    setProgressText('Submitting comparative benchmark suite to Python backend...');

    try {
      const res = await fetch('/api/benchmark', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nodes, rounds, seed })
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || `Benchmark returned status ${res.status}`);
      }

      const data = await res.json();
      setProgressText('Executing comparative benchmark scenarios...');

      let attempts = 0;
      const maxAttempts = 300; // 90s timeout for full suite
      while (attempts < maxAttempts) {
        await new Promise(r => setTimeout(r, 400));
        const statusRes = await fetch(`/api/simulate/${data.job_id}/status`);
        if (statusRes.ok) {
          const statusData = await statusRes.json();
          if (statusData.status === 'completed' && statusData.results) {
            setBenchmarkResults(statusData.results);
            setBenchmarkLoading(false);
            setProgressText('');
            return;
          } else if (statusData.status === 'failed') {
            throw new Error(statusData.error || 'Benchmark run failed');
          }
        }
        attempts++;
      }
      throw new Error('Benchmark timed out waiting for backend response');
    } catch (err: any) {
      console.error('Benchmark error:', err);
      setError(err?.message || 'Benchmark failed. Ensure the FastAPI backend is running on port 8000.');
      setBenchmarkLoading(false);
      setProgressText('');
    }
  }, []);

  const reset = useCallback(() => {
    setLoading(false);
    setBenchmarkLoading(false);
    setError(null);
    setProgressText('');
  }, []);

  return {
    loading,
    benchmarkLoading,
    progressText,
    error,
    results,
    setResults,
    benchmarkResults,
    setBenchmarkResults,
    jobId,
    runSimulation,
    runBenchmark,
    reset
  };
}
