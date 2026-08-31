# WSN Energy-Harvesting Routing Simulator - Enhanced Version

This is an enhanced version of the WSN Energy-Harvesting Routing Simulator that provides a web-based interface for running simulations and analyzing results.

## Features

- **REST API Backend**: Run simulations and benchmarks via HTTP endpoints
- **React Frontend**: Interactive UI to configure and visualize simulations
- **Persistence**: Simulation runs are saved to a SQLite database for later comparison
- **Visualization**: Network topology, charts, and time-series data
- **Benchmarking**: Run the standard 5-scenario comparison with one click

## Architecture

The enhanced version consists of two parts:

1. **Backend Service** (`backend/` directory): A FastAPI application that wraps the existing simulator without modifying any code in the `src/` directory.
2. **Frontend Application** (`frontend/` directory): A React application that consumes the backend API.

The existing simulator code in `src/` remains completely untouched.

## Prerequisites

- Python 3.8+
- Node.js 14+ and npm
- Git (to clone the repository if not already done)

## Installation

### Backend

1. Navigate to the backend directory:
   ```bash
   cd WSN_proj/backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Frontend

1. Navigate to the frontend directory:
   ```bash
   cd WSN_proj/frontend
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

## Running the Application

### Step 1: Start the Backend Server

In the backend directory, start the FastAPI server:

```bash
cd WSN_proj/backend
python main.py
```

The server will be available at `http://localhost:8000`.

You can verify it's running by visiting:
- Health check: `http://localhost:8000/health`
- API documentation: `http://localhost:8000/docs`

### Step 2: Start the Frontend Development Server

In a new terminal window, navigate to the frontend directory and start the development server:

```bash
cd WSN_proj/frontend
npm start
```

The frontend will be available at `http://localhost:3000`.

## Usage

1. Open your browser to `http://localhost:3000`
2. Use the control panel on the left to adjust simulation parameters:
   - Number of nodes, rounds, field size
   - Initial energy and battery capacity
   - Energy harvesting profile (none, constant, solar, stochastic)
   - Routing algorithm and feature toggles
3. Click "Run Simulation" to start a simulation
4. Wait for the simulation to complete (time depends on configuration)
5. View the results in the Results, Network View, and Charts tabs
6. Use the "Run Benchmark" button to run the standard 5-scenario comparison
7. Past simulations are saved and can be viewed in the history (to be implemented in later phases)

## API Endpoints

The backend provides the following endpoints:

- `POST /simulate`: Start a new simulation with the given configuration
- `GET /simulate/{job_id}/status`: Get the status and results of a simulation job
- `POST /benchmark`: Run the standard 5-scenario benchmark
- `GET /runs`: List recent simulation runs
- `GET /health`: Health check endpoint

## Project Structure

```
WSN_proj/
├── backend/                 # FastAPI backend service
│   ├── main.py              # Application entry point
│   ├── core/                # Core logic (simulator wrapper)
│   ├── api/                 # API route definitions
│   ├── db/                  # Database models and session handling
│   └── tasks/               # Background task definitions
├── frontend/                # React frontend application
│   ├── public/              # Static assets
│   └── src/                 # React source code
│       ├── components/      # Reusable UI components
│       ├── hooks/           # Custom React hooks
│       ├── utils/           # Utility functions and constants
│       └── App.js           # Main application component
├── src/                     # Original simulator code (LEFT UNTOUCHED)
│   ├── network.py           # Network topology and node representation
│   ├── energy_model.py      # Energy consumption model
│   ├── harvesting_model.py  # Energy harvesting models
│   ├── clustering.py        # Cluster formation logic
│   ├── routing.py           # Path finding and rerouting
│   ├── dp_lifetime.py       # Dynamic programming routing algorithms
│   ├── simulator.py         # Main simulation engine
│   └── visualize.py         # Visualization utilities
├── requirements.txt         # Python dependencies
├── package.json             # Node.js dependencies (frontend)
└── README.md                # Original project README
```

## Notes

- The backend uses an in-memory job store for simplicity. In a production environment, you would want to use Redis or a proper task queue like Celery.
- The frontend uses React Recharts for data visualization and D3.js for network topology rendering.
- All simulation logic is reused from the original simulator - no changes were made to any file in the `src/` directory.
- The enhancement follows a 5-phase approach as outlined in the plan file:
  1. Backend service with API and persistence
  2. Frontend MVP with parameter control and basic charts
  3. Process visualization (scrubber, heatmap, benchmark)
  4. Decision-support features (history, cost estimator, placement editor)
  5. Polish and documentation

## Troubleshooting

- If the backend fails to start, check that all Python dependencies are installed correctly.
- If the frontend fails to compile, check that all Node.js dependencies are installed.
- Make sure ports 8000 (backend) and 3000 (frontend) are available and not blocked by firewalls.
- For detailed logs, check the console output of each server.

## License

This project is licensed under the MIT License - see the original LICENSE file for details.

## Acknowledgements

This enhanced version builds upon the original WSN Energy-Harvesting Routing Simulator created by Santhosh Vellore.