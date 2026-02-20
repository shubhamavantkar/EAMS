from __future__ import annotations

import logging
import re
from datetime import datetime

import tldextract

from eams.models.events import ActivityEvent

LOGGER = logging.getLogger("eams.domain_tracker")

BROWSER_NAMES = {"chrome.exe", "msedge.exe", "firefox.exe", "brave.exe", "opera.exe"}
DOMAIN_RE = re.compile(r"([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}")


class DomainTracker:
    def parse_domain(self, app_name: str, title: str) -> str | None:
        if app_name.lower() not in BROWSER_NAMES:
            return None
        match = DOMAIN_RE.search(title)
        if not match:
            return None
        ext = tldextract.extract(match.group(0))
        if not ext.domain:
            return None
        return ".".join([p for p in [ext.domain, ext.suffix] if p])

    def event_from_app(self, app_name: str, title: str) -> ActivityEvent | None:
        try:
            domain = self.parse_domain(app_name, title)
            if not domain:
                return None
            return ActivityEvent(
                timestamp=datetime.now(),
                event_type="browser_domain",
                source="browser_tracker",
                payload={"domain": domain, "app_name": app_name},
            )
        except Exception:
            LOGGER.exception("Failed extracting browser domain")
            return None
