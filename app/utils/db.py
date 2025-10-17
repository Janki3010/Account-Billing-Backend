from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.settings import settings
from contextlib import contextmanager
import os

# Global engine - will be recreated in each process
engine = None
SessionLocal = None

def get_engine():
    """Get or create engine for current process"""
    global engine, SessionLocal
    if engine is None:
        engine = create_engine(
            settings.PG_CONN_STR,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={"keepalives": 1, "keepalives_idle": 30}
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine

def dispose_engine():
    """Dispose engine connections for multiprocessing"""
    global engine
    if engine is not None:
        engine.dispose(close=False)  # Critical for multiprocessing

def worker_init():
    """Initialize worker process - dispose parent's database connections"""
    dispose_engine()
    print(f"Worker process {os.getpid()} initialized")

@contextmanager
def get_db():
    """Get database session"""
    if SessionLocal is None:
        get_engine()
    
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()