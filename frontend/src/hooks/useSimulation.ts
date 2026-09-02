import { useState, useCallback, useRef } from 'react';
import { SimulationConfig, SimulationResults, BenchmarkResults } from '../types';
import { WsnSimulator } from '../engine/simulator';
import { runComprehensiveBenchmark } from '../engine/benchmark';

export function useSimulation() {
  const [loading, setLoading] = useState<boolean>(false);
  const [progressText, setProgressText] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<SimulationResults | null>(null);
  const [benchmarkResults, setBenchmarkResults] = useState<BenchmarkResults | null>(null);
  const [benchmarkLoading, setBenchmarkLoading] = useState<boolean>(false);
  const [jobId, setJobId] = useState<string | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);

  const runSimulation = useCallback(async (config: SimulationConfig) => {
    setLoading(true);
    setError(null);
    setProgressText('Initializing WSN simulation...');

    try {
      // First try backend API endpoint
      try {
        const res = await fetch('/api/simulate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(config)
        });

        if (res.ok) {
          const data = await res.json();
          setJobId(data.job_id);
          setProgressText('Running simulation in background...');

          // Poll status
          let attempts = 0;
          while (attempts < 60) {
            await new Promise(r => setTimeout(r, 250));
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
        }
      } catch (backendErr) {
        console.warn('Backend API unavailable or slow, executing with local engine:', backendErr);
      }

      // High-performance client-side simulation engine
      setProgressText('Simulating rounds with local engine...');
      await new Promise(r => setTimeout(r, 20)); // allow UI tick
      const sim = new WsnSimulator(config);
      const simResult = sim.run();
      setResults(simResult);
      setJobId('local_' + Date.now());
      setLoading(false);
      setProgressText('');
    } catch (err: any) {
      setError(err?.message || 'Simulation encountered an error');
      setLoading(false);
      setProgressText('');
    }
  }, []);

  const runBenchmark = useCallback(async (nodes: number = 50, rounds: number = 300, seed: number = 42) => {
    setBenchmarkLoading(true);
    setError(null);
    setProgressText('Running 9-scenario comparative benchmark suite...');

    try {
      try {
        const res = await fetch('/api/benchmark', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ nodes, rounds, seed })
        });

        if (res.ok) {
          const data = await res.json();
          let attempts = 0;
          while (attempts < 80) {
            await new Promise(r => setTimeout(r, 300));
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
        }
      } catch (bErr) {
        console.warn('Backend benchmark API failed, falling back to local runner:', bErr);
      }

      // Local runner fallback
      await new Promise(r => setTimeout(r, 20));
      const bench = runComprehensiveBenchmark(nodes, rounds, seed);
      setBenchmarkResults(bench);
      setBenchmarkLoading(false);
      setProgressText('');
    } catch (err: any) {
      setError(err?.message || 'Benchmark failed');
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
