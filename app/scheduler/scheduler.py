from apscheduler.schedulers.background import BackgroundScheduler
from functools import lru_cache

from app.services.reminders import rebuild_schedule as _rebuild


@lru_cache(maxsize=1)
def get_scheduler() -> BackgroundScheduler:
    return BackgroundScheduler(timezone="UTC")


async def rebuild_schedule(scheduler: BackgroundScheduler):
    await _rebuild(scheduler)
