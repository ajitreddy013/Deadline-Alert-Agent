import asyncio
from typing import Dict
from playwright.async_api import async_playwright
from app.core.config import settings
import os
import hashlib
from datetime import datetime
from dateutil import tz

from app.core.db import SessionLocal
from app.models.deadline import Deadline, StatusEnum, PriorityEnum, SourceEnum
from app.models.reminder_rule import ReminderRule, ChannelEnum
from app.scheduler.scheduler import get_scheduler
from app.services.reminders import schedule_for_deadline
from .parser import detect_deadline

_status: Dict[str, object] = {"running": False, "message": None}
_runner_task: asyncio.Task | None = None
_processed_hashes: set[str] = set()


def get_status() -> Dict[str, object]:
    return dict(_status)


async def ensure_runner_started():
    global _runner_task
    if _status["running"] and _runner_task and not _runner_task.done():
        return
    _runner_task = asyncio.create_task(_runner())


async def stop_runner():
    global _runner_task
    if _runner_task and not _runner_task.done():
        _runner_task.cancel()
        try:
            await _runner_task
        except asyncio.CancelledError:
            pass
    _status["running"] = False
    _status["message"] = "stopped"


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()


async def _runner():
    _status["running"] = True
    _status["message"] = "starting"
    user_data_dir = os.path.expanduser(settings.whatsapp_user_data_dir)
    os.makedirs(user_data_dir, exist_ok=True)

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=settings.whatsapp_headless,
                args=["--disable-gpu", "--no-sandbox"],
            )
            page = await browser.new_page()
            await page.goto("https://web.whatsapp.com/")
            await page.wait_for_load_state("domcontentloaded")
            _status["message"] = "whatsapp web loaded"

            # Periodically pull recent visible messages and parse
            while True:
                try:
                    texts = await page.eval_on_selector_all(
                        "span.selectable-text, div.selectable-text",
                        "els => els.slice(-40).map(e => e.innerText)",
                    )
                except Exception:
                    texts = []

                for t in texts:
                    h = _hash_text(t)
                    if h in _processed_hashes:
                        continue
                    _processed_hashes.add(h)
                    parsed = detect_deadline(t)
                    if not parsed:
                        continue

                    # Create deadline in DB
                    with SessionLocal() as db:
                        due_at = parsed["due_at"]
                        if due_at.tzinfo is None:
                            # Assume local tz then convert to aware
                            local_tz = tz.tzlocal()
                            due_at = due_at.replace(tzinfo=local_tz)
                        item = Deadline(
                            title=parsed["title"],
                            description=parsed.get("description"),
                            due_at=due_at,
                            status=StatusEnum.pending,
                            priority=PriorityEnum.normal,
                            source=SourceEnum.whatsapp,
                            confidence=parsed.get("confidence"),
                        )
                        db.add(item)
                        db.flush()
                        for offs in settings.default_reminder_offsets:
                            db.add(ReminderRule(deadline_id=item.id, offset_seconds=offs, channel=ChannelEnum.desktop, enabled=True))
                            db.add(ReminderRule(deadline_id=item.id, offset_seconds=offs, channel=ChannelEnum.mobile, enabled=True))
                        db.commit()
                        db.refresh(item)

                        # Schedule reminders for this deadline
                        scheduler = get_scheduler()
                        schedule_for_deadline(scheduler, item)

                await asyncio.sleep(5)
    except asyncio.CancelledError:
        _status["message"] = "cancelled"
    except Exception as e:
        _status["message"] = f"error: {e}"
    finally:
        _status["running"] = False
