"""
SQLAlchemy models for storing simulation runs and results.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class SimulationRun(Base):
    """Store simulation run configuration and summary."""
    __tablename__ = 'simulation_runs'

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    parameters = Column(Text)  # JSON string of simulation parameters
    summary = Column(Text)     # JSON string of simulation summary
    status = Column(String(20), default='completed')  # pending, running, completed, failed
    job_id = Column(String(36), unique=True, index=True)  # UUID

class SimulationResult(Base):
    """Store time-series results for detailed analysis."""
    __tablename__ = 'simulation_results'

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, index=True)  # Foreign key to simulation_runs
    round_number = Column(Integer)
    alive_nodes = Column(Integer)
    total_energy = Column(Float)
    harvested_energy = Column(Float, default=0.0)
    reroute_events = Column(Integer, default=0)
    # Per-node energy could be stored in a separate table or as JSON if needed

# For simplicity, we'll store detailed time-series as JSON in the SimulationRun table
# In a production system with large datasets, we'd normalize this properly