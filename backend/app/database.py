"""Synchronous SQLAlchemy session management; SQLite locally, PostgreSQL in Docker."""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool

def normalize_database_url(url: str) -> str:
    """Use the installed psycopg v3 driver for conventional hosted Postgres URLs."""
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


if os.getenv("APP_ENV") == "production" and not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is required in production; do not use ephemeral SQLite")

DATABASE_URL = normalize_database_url(os.getenv("DATABASE_URL", "sqlite:///./tracker.db"))
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
