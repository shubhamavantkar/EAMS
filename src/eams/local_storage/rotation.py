from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path


class RotationPolicy:
    def __init__(self, retention_days: int) -> None:
        self.retention_days = retention_days

    def prune(self, events_dir: Path) -> int:
        deleted = 0
        cutoff = datetime.now().date() - timedelta(days=self.retention_days)
        for file in events_dir.glob("events-*.log"):
            date_part = file.stem.replace("events-", "")
            try:
                created_day = datetime.fromisoformat(date_part).date()
            except ValueError:
                continue
            if created_day < cutoff:
                file.unlink(missing_ok=True)
                deleted += 1
        return deleted
