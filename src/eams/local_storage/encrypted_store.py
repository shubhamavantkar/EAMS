from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
from datetime import date
from pathlib import Path

from cryptography.fernet import Fernet

from eams.models.events import ActivityEvent

LOGGER = logging.getLogger("eams.encrypted_store")


class EncryptedEventStore:
    def __init__(self, events_dir: Path, key: str) -> None:
        self.events_dir = events_dir
        self.events_dir.mkdir(parents=True, exist_ok=True)
        self.fernet = Fernet(key.encode())
        self._hmac_key = key.encode()

    def _event_file(self, event_date: date) -> Path:
        return self.events_dir / f"events-{event_date.isoformat()}.log"

    def append_event(self, event: ActivityEvent) -> None:
        serialized = json.dumps(event.to_dict(), separators=(",", ":")).encode()
        token = self.fernet.encrypt(serialized)
        digest = hmac.new(self._hmac_key, token, hashlib.sha256).hexdigest().encode()
        line = base64.urlsafe_b64encode(token) + b"." + digest + b"\n"
        path = self._event_file(event.timestamp.date())
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("ab") as fh:
            fh.write(line)

    def read_day(self, day: date) -> list[dict]:
        path = self._event_file(day)
        if not path.exists():
            return []
        events: list[dict] = []
        with path.open("rb") as fh:
            for line in fh:
                try:
                    token_b64, digest = line.strip().split(b".", 1)
                    token = base64.urlsafe_b64decode(token_b64)
                    expected = hmac.new(self._hmac_key, token, hashlib.sha256).hexdigest().encode()
                    if not hmac.compare_digest(expected, digest):
                        LOGGER.warning("Integrity check failed for an event line")
                        continue
                    payload = self.fernet.decrypt(token)
                    events.append(json.loads(payload.decode()))
                except Exception:
                    LOGGER.exception("Skipping corrupt event line")
        return events
