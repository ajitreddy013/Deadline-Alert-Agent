from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.core.db import init_db
from app.core.config import settings
from app.scheduler.scheduler import get_scheduler, rebuild_schedule
from app.api.deadlines import router as deadlines_router
from app.api.ingestion import router as ingestion_router
from app.api.settings_api import router as settings_router


ALLOWED_ORIGINS = [
    "http://localhost",
    "http://127.0.0.1",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://10.0.2.2:8000",  # Android emulator reference to host
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure data dir exists
    os.makedirs("data", exist_ok=True)
    # Initialize DB
    init_db()
    # Start scheduler
    scheduler = get_scheduler()
    scheduler.start(paused=True)
    # Rebuild schedule from DB
    await rebuild_schedule(scheduler)
    scheduler.resume()
    try:
        yield
    finally:
        scheduler.shutdown(wait=False)


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev convenience; restrict later as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(deadlines_router, prefix="/deadlines", tags=["deadlines"])
app.include_router(ingestion_router, prefix="/ingestion", tags=["ingestion"])
app.include_router(settings_router, prefix="/settings", tags=["settings"])


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
