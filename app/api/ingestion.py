from fastapi import APIRouter
from pydantic import BaseModel
import asyncio

from app.integrations.whatsapp_web.runner import ensure_runner_started, stop_runner, get_status

router = APIRouter()


class IngestionStatus(BaseModel):
    running: bool
    message: str | None = None


@router.post("/whatsapp/start", response_model=IngestionStatus)
async def start_whatsapp_ingestion():
    asyncio.create_task(ensure_runner_started())
    status = get_status()
    return IngestionStatus(running=status["running"], message=status.get("message"))


@router.get("/whatsapp/status", response_model=IngestionStatus)
async def whatsapp_status():
    status = get_status()
    return IngestionStatus(running=status["running"], message=status.get("message"))


@router.post("/whatsapp/stop", response_model=IngestionStatus)
async def stop_whatsapp():
    await stop_runner()
    status = get_status()
    return IngestionStatus(running=status["running"], message=status.get("message"))
