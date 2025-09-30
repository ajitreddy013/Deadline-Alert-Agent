from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.config import settings

router = APIRouter()


class SettingsOut(BaseModel):
    app_name: str
    desktop_notifications_enabled: bool
    onesignal_enabled: bool
    whatsapp_headless: bool


@router.get("/", response_model=SettingsOut)
async def get_settings():
    return SettingsOut(
        app_name=settings.app_name,
        desktop_notifications_enabled=settings.desktop_notifications_enabled,
        onesignal_enabled=settings.onesignal_enabled,
        whatsapp_headless=settings.whatsapp_headless,
    )


@router.put("/")
async def put_settings():
    # TODO: Persist editable settings to local file and reload config.
    raise HTTPException(status_code=501, detail="Settings update not implemented yet")
