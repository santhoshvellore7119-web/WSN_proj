import express from 'express';
import path from 'path';
import { createServer as createViteServer } from 'vite';

const BACKEND_URL = process.env.BACKEND_URL || 'http://127.0.0.1:8000';
const PORT = parseInt(process.env.PORT || '3000', 10);

async function startServer() {
  const app = express();

  app.use(express.json({ limit: '15mb' }));

  // Proxy all /api requests directly to the Python FastAPI backend
  app.all('/api/*', async (req, res) => {
    const targetPath = req.url.replace(/^\/api/, '');
    const targetUrl = `${BACKEND_URL}${targetPath}`;

    try {
      const fetchOptions: RequestInit = {
        method: req.method,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      };

      if (['POST', 'PUT', 'PATCH'].includes(req.method) && Object.keys(req.body || {}).length > 0) {
        fetchOptions.body = JSON.stringify(req.body);
      }

      const backendRes = await fetch(targetUrl, fetchOptions);
      const data = await backendRes.json().catch(() => ({}));
      res.status(backendRes.status).json(data);
    } catch (err: any) {
      console.error(`Error forwarding request to backend (${targetUrl}):`, err.message);
      res.status(502).json({
        error: 'Backend service unavailable',
        detail: 'Ensure the FastAPI backend is running on port 8000 (uvicorn backend.main:app --port 8000)'
      });
    }
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
    console.log(`WSN Simulator frontend running on http://localhost:${PORT}`);
    console.log(`Proxying /api requests to FastAPI backend on ${BACKEND_URL}`);
  });
}

startServer();
