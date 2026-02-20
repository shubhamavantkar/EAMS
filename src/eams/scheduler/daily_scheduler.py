from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger


class DailyScheduler:
    def __init__(self) -> None:
        self.scheduler = BackgroundScheduler()

    def start_daily(self, hour: int, job, timezone: str | None = None) -> None:
        trigger = CronTrigger(hour=hour, minute=0, timezone=timezone)
        self.scheduler.add_job(job, trigger=trigger, id="daily_report", replace_existing=True)
        self.scheduler.start()

    def shutdown(self) -> None:
        self.scheduler.shutdown(wait=False)
