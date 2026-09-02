import express from 'express';
import path from 'path';
import { createServer as createViteServer } from 'vite';
import { WsnSimulator } from './src/engine/simulator';
import {
  runComprehensiveBenchmark,
  runScalabilitySweep,
  runHeterogeneitySweep
} from './src/engine/benchmark';
import { SimulationConfig, SavedRun } from './src/types';

interface JobRecord {
  job_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  config: any;
  created_at: string;
  completed_at?: string;
  results?: any;
  error?: string;
}

const jobsStore = new Map<string, JobRecord>();
const savedRunsStore: SavedRun[] = [];

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json({ limit: '15mb' }));

  // --- API Endpoints ---

  // Health check
  app.get('/api/health', (_req, res) => {
    res.json({
      status: 'healthy',
      service: 'WSN Energy-Harvesting Simulator API',
      timestamp: new Date().toISOString()
    });
  });

  // Start Simulation
  app.post('/api/simulate', (req, res) => {
    const config: SimulationConfig = req.body;
    const jobId = 'sim_' + Date.now() + '_' + Math.random().toString(36).substring(2, 7);

    const job: JobRecord = {
      job_id: jobId,
      status: 'pending',
      config,
      created_at: new Date().toISOString()
    };
    jobsStore.set(jobId, job);

    // Run simulation asynchronously
    setTimeout(() => {
      try {
        job.status = 'running';
        const sim = new WsnSimulator(config);
        const results = sim.run();
        job.status = 'completed';
        job.results = results;
        job.completed_at = new Date().toISOString();
      } catch (err: any) {
        job.status = 'failed';
        job.error = err?.message || 'Simulation execution error';
        job.completed_at = new Date().toISOString();
      }
    }, 10);

    res.json({
      job_id: jobId,
      status: 'pending',
      message: 'Simulation initiated'
    });
  });

  // Get Simulation Status
  app.get('/api/simulate/:jobId/status', (req, res) => {
    const { jobId } = req.params;
    const job = jobsStore.get(jobId);
    if (!job) {
      return res.status(404).json({ error: 'Job not found' });
    }
    res.json(job);
  });

  // Run Benchmark (9 Configurations)
  app.post('/api/benchmark', (req, res) => {
    const { nodes = 50, rounds = 300, seed = 42 } = req.body || {};
    const jobId = 'bench_' + Date.now() + '_' + Math.random().toString(36).substring(2, 7);

    const job: JobRecord = {
      job_id: jobId,
      status: 'pending',
      config: { nodes, rounds, seed, benchmark: true },
      created_at: new Date().toISOString()
    };
    jobsStore.set(jobId, job);

    setTimeout(() => {
      try {
        job.status = 'running';
        const results = runComprehensiveBenchmark(nodes, rounds, seed);
        job.status = 'completed';
        job.results = results;
        job.completed_at = new Date().toISOString();
      } catch (err: any) {
        job.status = 'failed';
        job.error = err?.message || 'Benchmark execution error';
        job.completed_at = new Date().toISOString();
      }
    }, 10);

    res.json({
      job_id: jobId,
      status: 'pending',
      message: 'Benchmark suite initiated'
    });
  });

  // Run Scalability Sweep
  app.post('/api/experiments/scalability', (req, res) => {
    const { nodeCounts = [20, 50, 80, 120, 160], rounds = 150, seed = 42 } = req.body || {};
    try {
      const results = runScalabilitySweep(nodeCounts, rounds, seed);
      res.json({ success: true, points: results });
    } catch (err: any) {
      res.status(500).json({ error: err?.message || 'Scalability sweep failed' });
    }
  });

  // Run Heterogeneity Sweep
  app.post('/api/experiments/heterogeneity', (req, res) => {
    const { shadowFractions = [0.0, 0.2, 0.4, 0.6, 0.8], nodes = 50, rounds = 150, seed = 42 } = req.body || {};
    try {
      const results = runHeterogeneitySweep(shadowFractions, nodes, rounds, seed);
      res.json({ success: true, points: results });
    } catch (err: any) {
      res.status(500).json({ error: err?.message || 'Heterogeneity sweep failed' });
    }
  });

  // List saved runs
  app.get('/api/runs', (_req, res) => {
    res.json(savedRunsStore);
  });

  // Save run
  app.post('/api/runs/save', (req, res) => {
    const { name, config, summary, results } = req.body;
    const newRun: SavedRun = {
      id: 'run_' + Date.now(),
      name: name || `Simulation (${config?.nodes || 50} nodes, ${config?.rounds || 200} rds)`,
      createdAt: new Date().toISOString(),
      config,
      summary,
      results
    };
    savedRunsStore.unshift(newRun);
    if (savedRunsStore.length > 50) savedRunsStore.pop(); // keep last 50
    res.json({ success: true, run: newRun });
  });

  // Delete saved run
  app.delete('/api/runs/:id', (req, res) => {
    const { id } = req.params;
    const idx = savedRunsStore.findIndex(r => r.id === id);
    if (idx !== -1) {
      savedRunsStore.splice(idx, 1);
    }
    res.json({ success: true });
  });

  // --- Vite / Static Middleware Setup ---
  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa'
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (_req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`WSN Simulator server running on http://localhost:${PORT}`);
  });
}

startServer();
