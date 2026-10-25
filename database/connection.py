"""
Database connection and session lifecycle management using SQLAlchemy.
"""
import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path
import config

DB_FILE = config.DB_PATH
ENGINE = create_engine(
    f"sqlite:///{DB_FILE}",
    connect_args={"check_same_thread": False},
    echo=False
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=ENGINE,
    expire_on_commit=False
)
Base = declarative_base()

def init_db():
    """Create all tables in the SQLite database if they don't already exist."""
    from database import models  # ensure models are imported
    Base.metadata.create_all(bind=ENGINE)

@contextmanager
def get_db():
    """Provide a transactional database session scope."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
