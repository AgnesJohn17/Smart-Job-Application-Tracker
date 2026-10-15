"""Synchronous SQLAlchemy session management; SQLite locally, PostgreSQL in Docker."""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tracker.db")
sqlite = DATABASE_URL.startswith("sqlite")
kwargs = {"connect_args": {"check_same_thread": False}} if sqlite else {"pool_pre_ping": True}
if DATABASE_URL in ("sqlite://", "sqlite:///:memory:"):
    kwargs["poolclass"] = StaticPool
engine = create_engine(DATABASE_URL, **kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    with SessionLocal() as session:
        yield session
