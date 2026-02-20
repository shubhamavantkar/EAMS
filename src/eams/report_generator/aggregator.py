from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from eams.models.events import ReportSummary


def aggregate_day(events: list[dict], endpoint_id: str, date_str: str) -> ReportSummary:
    app_usage = defaultdict(int)
    domain_usage = defaultdict(int)
    logins: list[str] = []
    logouts: list[str] = []
    active_seconds = 0
    idle_seconds = 0

    last_ts = None
    last_app = None
    last_state = "active"
    last_domain = None

    for event in sorted(events, key=lambda e: e.get("timestamp", "")):
        ts = datetime.fromisoformat(event["timestamp"])
        if last_ts:
            delta = int((ts - last_ts).total_seconds())
            if delta > 0:
                if last_state == "idle":
                    idle_seconds += delta
                else:
                    active_seconds += delta
                    if last_app:
                        app_usage[last_app] += delta
                    if last_domain:
                        domain_usage[last_domain] += delta
        if event["event_type"] == "active_app":
            last_app = event["payload"].get("app_name")
        elif event["event_type"] == "state_change":
            last_state = event["payload"].get("state", "active")
        elif event["event_type"] == "browser_domain":
            last_domain = event["payload"].get("domain")
        elif event["event_type"] == "user_login":
            logins.append(event["timestamp"])
        elif event["event_type"] == "user_logout":
            logouts.append(event["timestamp"])
        last_ts = ts

    return ReportSummary(
        date=date_str,
        endpoint_id=endpoint_id,
        total_active_seconds=active_seconds,
        total_idle_seconds=idle_seconds,
        app_usage_seconds=dict(sorted(app_usage.items(), key=lambda x: x[1], reverse=True)),
        browser_domain_seconds=dict(sorted(domain_usage.items(), key=lambda x: x[1], reverse=True)),
        login_events=logins,
        logout_events=logouts,
    )
