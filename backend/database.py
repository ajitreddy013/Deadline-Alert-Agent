from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from backend/.env if present
load_dotenv()

# Default to a stable SQLite file under backend/tasks.db
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_SQLITE_PATH = (BASE_DIR / "tasks.db").as_posix()
DEFAULT_DB_URL = f"sqlite:///{DEFAULT_SQLITE_PATH}"

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)

# Ensure SQLite uses proper connect args
connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
