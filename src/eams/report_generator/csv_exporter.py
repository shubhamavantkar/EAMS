from __future__ import annotations

import csv
from pathlib import Path

from eams.models.events import ReportSummary


def write_csv(summary: ReportSummary, out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["date", summary.date])
        writer.writerow(["endpoint_id", summary.endpoint_id])
        writer.writerow(["total_active_seconds", summary.total_active_seconds])
        writer.writerow(["total_idle_seconds", summary.total_idle_seconds])
        writer.writerow([])
        writer.writerow(["top_applications", "seconds"])
        for app, sec in list(summary.app_usage_seconds.items())[:10]:
            writer.writerow([app, sec])
        writer.writerow([])
        writer.writerow(["browser_domains", "seconds"])
        for domain, sec in summary.browser_domain_seconds.items():
            writer.writerow([domain, sec])
        writer.writerow([])
        writer.writerow(["login_events"])
        for ts in summary.login_events:
            writer.writerow([ts])
        writer.writerow(["logout_events"])
        for ts in summary.logout_events:
            writer.writerow([ts])
    return out_path
