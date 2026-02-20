from __future__ import annotations

import logging
import queue
import threading
import time
from datetime import date, datetime
from pathlib import Path

from eams.activity_collector.idle_monitor import IdleMonitor
from eams.app_tracker.foreground_tracker import ForegroundTracker
from eams.browser_tracker.domain_tracker import DomainTracker
from eams.config import Settings
from eams.email_service.smtp_sender import SMTPSender
from eams.local_storage.encrypted_store import EncryptedEventStore
from eams.local_storage.rotation import RotationPolicy
from eams.report_generator.aggregator import aggregate_day
from eams.report_generator.csv_exporter import write_csv
from eams.report_generator.html_renderer import render_html
from eams.scheduler.daily_scheduler import DailyScheduler
from eams.models.events import ActivityEvent
from eams.system_events.windows_events import SystemEventsCollector

LOGGER = logging.getLogger("eams.supervisor")


class ServiceSupervisor:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.stop_event = threading.Event()
        self.queue: queue.Queue = queue.Queue(maxsize=1000)

        self.data_dir = settings.data_dir
        self.events_dir = self.data_dir / "events"
        self.reports_dir = self.data_dir / "reports"

        self.storage = EncryptedEventStore(self.events_dir, settings.storage_key)
        self.rotator = RotationPolicy(settings.retention_days)
        self.idle_monitor = IdleMonitor(settings.idle_threshold_seconds)
        self.app_tracker = ForegroundTracker()
        self.domain_tracker = DomainTracker()
        self.system_events = SystemEventsCollector()
        self.scheduler = DailyScheduler()
        self.sender = SMTPSender(
            settings.smtp_host,
            settings.smtp_port,
            settings.smtp_username,
            settings.smtp_password,
            settings.smtp_use_tls,
        )

    def enqueue_event(self, event) -> None:
        try:
            self.queue.put_nowait(event)
        except queue.Full:
            LOGGER.warning("Event queue full; dropping event")

    def collector_loop(self) -> None:
        for event in self.system_events.startup_events():
            self.enqueue_event(event)

        while not self.stop_event.is_set():
            try:
                idle_event = self.idle_monitor.poll_event()
                if idle_event:
                    self.enqueue_event(idle_event)

                app_event = self.app_tracker.poll_event()
                if app_event:
                    self.enqueue_event(app_event)
                    domain_event = self.domain_tracker.event_from_app(
                        app_event.payload.get("app_name", ""),
                        app_event.payload.get("window_title", ""),
                    )
                    if domain_event:
                        self.enqueue_event(domain_event)
            except Exception:
                LOGGER.exception("Collector loop error")
            time.sleep(self.settings.poll_seconds)

        self.enqueue_event(self.system_events.shutdown_event())

    def storage_loop(self) -> None:
        while not self.stop_event.is_set() or not self.queue.empty():
            try:
                event = self.queue.get(timeout=1)
            except queue.Empty:
                continue
            try:
                self.storage.append_event(event)
            except Exception:
                LOGGER.exception("Failed to persist event")

    def generate_and_send_report(self, day: date | None = None) -> None:
        report_day = day or date.today()
        events = self.storage.read_day(report_day)
        summary = aggregate_day(events, endpoint_id=self.settings.endpoint_id, date_str=report_day.isoformat())

        csv_path = write_csv(summary, self.reports_dir / f"report-{report_day.isoformat()}.csv")
        html_body = render_html(summary, Path(__file__).resolve().parents[1] / "templates")
        result = self.sender.send_daily_report(
            recipient=self.settings.recipient_email,
            subject=f"EAMS Daily Report - {self.settings.endpoint_id} - {report_day.isoformat()}",
            html_body=html_body,
            csv_path=csv_path,
        )

        self.enqueue_event(
            ActivityEvent(
                timestamp=datetime.now(),
                event_type="email_delivery",
                source="email_service",
                payload={"success": result.success, "error": result.error_message},
            )
        )
        LOGGER.info("Report send status: %s", result.success)

    def start(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        collector = threading.Thread(target=self.collector_loop, daemon=True)
        storer = threading.Thread(target=self.storage_loop, daemon=True)
        collector.start()
        storer.start()

        self.scheduler.start_daily(self.settings.report_hour, self.generate_and_send_report)
        LOGGER.info("Service supervisor started")

        try:
            while not self.stop_event.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            LOGGER.info("Received interrupt, stopping")
        finally:
            self.stop_event.set()
            collector.join(timeout=5)
            storer.join(timeout=5)
            self.rotator.prune(self.events_dir)
            self.scheduler.shutdown()
