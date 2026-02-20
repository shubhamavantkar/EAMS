from __future__ import annotations

import logging
import platform
from datetime import datetime

from eams.models.events import ActivityEvent

LOGGER = logging.getLogger("eams.foreground_tracker")

try:
    import psutil
except Exception:  # pragma: no cover
    psutil = None

if platform.system() == "Windows":
    try:
        import win32gui
        import win32process
    except Exception:  # pragma: no cover
        win32gui = None
        win32process = None
else:
    win32gui = None
    win32process = None


class ForegroundTracker:
    def __init__(self) -> None:
        self._last_app: str | None = None

    def _read_foreground_windows(self) -> tuple[str, str]:
        if not (win32gui and win32process and psutil):
            return ("unknown", "")
        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd) or ""
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        name = psutil.Process(pid).name()
        return name, title

    def poll_event(self) -> ActivityEvent | None:
        try:
            app_name, title = self._read_foreground_windows()
        except Exception:
            LOGGER.exception("Failed to read foreground app")
            return None

        if app_name != self._last_app:
            self._last_app = app_name
            return ActivityEvent(
                timestamp=datetime.now(),
                event_type="active_app",
                source="app_tracker",
                payload={"app_name": app_name, "window_title": title},
            )
        return None
