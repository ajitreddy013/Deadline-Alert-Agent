from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select
from apscheduler.schedulers.background import BackgroundScheduler

from app.core.db import SessionLocal
from app.core.config import settings
from app.models.deadline import Deadline
from app.models.reminder_rule import ReminderRule, ChannelEnum
from app.integrations.notifications.mac import notify as mac_notify
from app.integrations.notifications.onesignal import send as onesignal_send


async def rebuild_schedule(scheduler: BackgroundScheduler):
    with SessionLocal() as db:
        _schedule_all(db, scheduler)


def _schedule_all(db: Session, scheduler: BackgroundScheduler):
    now = datetime.now(timezone.utc)
    deadlines = db.execute(select(Deadline)).scalars().all()

    for d in deadlines:
        schedule_for_deadline(scheduler, d, now)


def schedule_for_deadline(scheduler: BackgroundScheduler, d: Deadline, now: datetime | None = None):
    if now is None:
        now = datetime.now(timezone.utc)
    for r in d.reminder_rules:
        trigger_at = (d.due_at - timedelta(seconds=abs(r.offset_seconds))) if r.offset_seconds <= 0 else (d.due_at + timedelta(seconds=r.offset_seconds))
        if trigger_at <= now or not r.enabled:
            continue
        job_id = f"reminder:{d.id}:{r.id}:{r.channel}"
        scheduler.add_job(
            _trigger_reminder,
            "date",
            id=job_id,
            run_date=trigger_at,
            args=[d.id, r.id, r.channel],
            replace_existing=True,
        )


def _trigger_reminder(deadline_id: str, rule_id: str, channel: ChannelEnum):
    with SessionLocal() as db:
        d = db.get(Deadline, deadline_id)
        if not d:
            return
        title = d.title
        due_str = d.due_at.astimezone().strftime("%Y-%m-%d %H:%M")
        body = f"Due {due_str}"

        if channel == ChannelEnum.desktop and settings.desktop_notifications_enabled:
            mac_notify(title=title, message=body)
        elif channel == ChannelEnum.mobile and settings.onesignal_enabled:
            onesignal_send(title=title, message=body)
        # WhatsApp outbound via Twilio can be added later
