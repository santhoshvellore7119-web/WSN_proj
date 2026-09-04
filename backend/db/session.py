"""
Database session handling for SQLite.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from .models import Base

# Database URL - SQLite file in the backend directory
DATABASE_URL = "sqlite:///./wsn_simulator.db"

# Create engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize the database - create tables if they don't exist."""
    Base.metadata.create_all(bind=engine)

# Auto-initialize tables
init_db()

def get_db_session():
    """Get a database session."""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Caller should close the session

# For use as a context manager
def get_db():
    """Dependency for FastAPI to get DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()