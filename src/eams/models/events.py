from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict


@dataclass(frozen=True)
class ActivityEvent:
    timestamp: datetime
    event_type: str
    source: str
    payload: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


@dataclass
class ReportSummary:
    date: str
    endpoint_id: str
    total_active_seconds: int
    total_idle_seconds: int
    app_usage_seconds: dict[str, int]
    browser_domain_seconds: dict[str, int]
    login_events: list[str]
    logout_events: list[str]
