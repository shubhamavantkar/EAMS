from __future__ import annotations

import ctypes
import logging
import platform
from ctypes import wintypes
from datetime import datetime

from eams.models.events import ActivityEvent

LOGGER = logging.getLogger("eams.idle_monitor")


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.UINT), ("dwTime", wintypes.DWORD)]


class IdleMonitor:
    def __init__(self, idle_threshold_seconds: int) -> None:
        self.idle_threshold_seconds = idle_threshold_seconds
        self._last_state = "active"

    def _get_idle_seconds_windows(self) -> int:
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        info = LASTINPUTINFO()
        info.cbSize = ctypes.sizeof(info)
        if not user32.GetLastInputInfo(ctypes.byref(info)):
            return 0
        millis = kernel32.GetTickCount() - info.dwTime
        return int(millis / 1000)

    def get_idle_seconds(self) -> int:
        if platform.system() == "Windows":
            try:
                return self._get_idle_seconds_windows()
            except Exception:
                LOGGER.exception("Failed to read idle time")
        return 0

    def poll_event(self) -> ActivityEvent | None:
        idle_seconds = self.get_idle_seconds()
        state = "idle" if idle_seconds >= self.idle_threshold_seconds else "active"
        if state != self._last_state:
            self._last_state = state
            return ActivityEvent(
                timestamp=datetime.now(),
                event_type="state_change",
                source="activity_collector",
                payload={"state": state, "idle_seconds": idle_seconds},
            )
        return None
