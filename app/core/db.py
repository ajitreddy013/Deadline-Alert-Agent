from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
import os

Base = declarative_base()


def get_engine():
    # Ensure directory for SQLite exists
    url = settings.database_url
    if url.startswith("sqlite"):
        os.makedirs("data", exist_ok=True)
        connect_args = {"check_same_thread": False}
    else:
        connect_args = {}
    return create_engine(url, echo=False, future=True, connect_args=connect_args)


engine = get_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db():
    from app.models import deadline, reminder_rule  # noqa: F401
    Base.metadata.create_all(bind=engine)


# Dependency for FastAPI routes
from typing import Generator

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
