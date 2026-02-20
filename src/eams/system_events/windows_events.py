from __future__ import annotations

from datetime import datetime

import psutil

from eams.models.events import ActivityEvent


class SystemEventsCollector:
    def startup_events(self) -> list[ActivityEvent]:
        boot = datetime.fromtimestamp(psutil.boot_time())
        now = datetime.now()
        return [
            ActivityEvent(timestamp=boot, event_type="system_boot", source="system_events", payload={}),
            ActivityEvent(timestamp=now, event_type="user_login", source="system_events", payload={}),
        ]

    def shutdown_event(self) -> ActivityEvent:
        return ActivityEvent(timestamp=datetime.now(), event_type="user_logout", source="system_events", payload={})
