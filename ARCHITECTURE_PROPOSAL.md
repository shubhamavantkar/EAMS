# Employee Activity Monitoring System (Python) — Architecture Proposal (No Code)

## 1) System Architecture Design

### Design Goals
- **Production-safe background agent** for Windows 10/11 endpoints.
- **Ethical boundaries**: collect only activity metadata, never content/keystrokes.
- **Low overhead**: event-driven/polling hybrid with bounded intervals.
- **Resilience**: crash isolation between modules, local durability, retry-based reporting.
- **Security**: encrypted at-rest local logs, secrets from environment, minimal privilege.

### High-Level Architecture
The system is a **single endpoint agent** with modular services running in-process (MVP), each behind clear interfaces. A central `service_runner` composes dependencies and controls lifecycle.

Core runtime components:
1. **Collectors**
   - `activity_collector`: idle/active state from user input inactivity.
   - `app_tracker`: foreground window polling + app duration accumulation.
   - `browser_tracker`: domain extraction only from browser window titles/URLs when available.
   - `system_events`: boot/login/logout/shutdown event capture.
2. **Storage Layer**
   - `local_storage`: encrypted append-only event log + integrity checks + rotation.
3. **Aggregation & Reporting**
   - `report_generator`: daily summaries, top apps, browser domain totals, CSV + HTML output.
4. **Delivery Layer**
   - `email_service`: SMTP TLS sender with retries/backoff.
5. **Orchestration**
   - `scheduler`: triggers 6:00 PM daily report and rollover tasks.
   - `service_runner`: startup wiring, health monitoring, graceful shutdown.

### Textual Data Flow Diagram
```
[OS Signals + Window State + Input Idle]
          │
          ▼
[activity_collector | app_tracker | browser_tracker | system_events]
          │ normalized ActivityEvent objects
          ▼
[local_storage]
  - encrypt event record
  - append to daily log
  - rotate + checksum
          │
          ├──(on schedule: 18:00 local)
          ▼
[report_generator]
  - decrypt/read day logs
  - aggregate active vs idle
  - compute app/domain usage
  - build HTML + CSV artifacts
          │
          ▼
[email_service]
  - SMTP AUTH over TLS
  - send HTML body + CSV attachment
  - retry with exponential backoff
          │
          ▼
[delivery status event -> local_storage]
```

### Module Interactions
- Collectors emit immutable `ActivityEvent` DTOs to a lightweight in-memory queue.
- Storage consumer persists events durably and acknowledges queue entries.
- Scheduler invokes report generation for the current workday at configured local time (default 18:00).
- Email service returns structured send result (`success`, `attempts`, `error_code`).
- Service runner records health heartbeats and supervises worker threads.

### Reliability Strategy
- **Per-module exception boundaries**: failures logged and isolated; no full-agent crash.
- **Write-ahead buffering**: short memory queue + periodic flush to encrypted storage.
- **Idempotent reporting**: report keyed by date + endpoint ID to avoid duplicate sends.
- **Retry policy**: bounded exponential backoff; final failure persisted for next cycle.
- **Graceful stop hooks**: final flush on SIGTERM/service stop.

### Security & Privacy Controls
- Allowed data: timestamps, app executable/window title metadata, idle durations, browser domain.
- Blocked data by design: keystrokes, clipboard, content payloads, file bodies.
- Storage encrypted with symmetric key (environment-managed).
- SMTP credentials loaded from environment or OS secret store abstraction.
- Logs redact secrets and PII-like tokens where possible.

---

## 2) Library / Technology Choices

### Runtime & Config
- **Python 3.11+**: modern typing/perf/support.
- **pydantic-settings** (or `python-dotenv` + dataclass): typed env/config management.
- **tenacity**: resilient retry/backoff for email delivery.
- **structlog** or stdlib `logging` + `RotatingFileHandler`: production logging.

### Windows Activity + Foreground App Detection
- **pywin32**: WinAPI access (`GetForegroundWindow`, session events, process metadata).
- **psutil**: process info, boot time, lightweight system state.
- **ctypes` + WinAPI GetLastInputInfo** (via pywin32/ctypes): idle-time measurement.

### Browser Domain Tracking
- **tldextract**: robust domain parsing (effective TLD handling).
- Browser source strategy (MVP): parse domain cues from active window title where possible; optionally enrich with browser-specific APIs later.

### Scheduling
- **APScheduler**: robust in-process cron-like scheduling with timezone support.

### Encryption & Integrity
- **cryptography (Fernet/AES-GCM)**: encrypted local event files.
- **hashlib/hmac**: integrity checksums for corruption detection.

### Reporting
- **pandas** (optional) or pure `csv` + `collections`: aggregation and CSV export.
- **jinja2**: HTML email template rendering.

### Email Transport
- stdlib **smtplib + ssl** for SMTP over TLS.
- `email.message.EmailMessage` for multipart HTML + attachment.

### Why these choices
- Mature, widely used libraries reduce operational risk.
- Windows-first API coverage with pywin32.
- Minimal dependencies for security footprint.
- Strong encryption primitives via `cryptography`.

---

## 3) Production-Ready Folder Structure

```text
employee-monitor/
├─ pyproject.toml
├─ requirements.txt
├─ README.md
├─ .env.example
├─ configs/
│  ├─ default.yaml
│  └─ logging.yaml
├─ scripts/
│  ├─ install_service.ps1
│  ├─ uninstall_service.ps1
│  └─ setup_startup_task.ps1
├─ data/                      # runtime-created (gitignored)
│  ├─ logs/
│  ├─ events/
│  └─ reports/
├─ src/
│  └─ eams/
│     ├─ __init__.py
│     ├─ main.py              # entrypoint for dev/prod mode
│     ├─ config.py
│     ├─ models/
│     │  ├─ __init__.py
│     │  ├─ events.py         # ActivityEvent, ReportSummary
│     │  └─ results.py        # SendResult, HealthStatus
│     ├─ activity_collector/
│     │  ├─ __init__.py
│     │  └─ idle_monitor.py
│     ├─ app_tracker/
│     │  ├─ __init__.py
│     │  └─ foreground_tracker.py
│     ├─ browser_tracker/
│     │  ├─ __init__.py
│     │  └─ domain_tracker.py
│     ├─ system_events/
│     │  ├─ __init__.py
│     │  └─ windows_events.py
│     ├─ local_storage/
│     │  ├─ __init__.py
│     │  ├─ encrypted_store.py
│     │  └─ rotation.py
│     ├─ report_generator/
│     │  ├─ __init__.py
│     │  ├─ aggregator.py
│     │  ├─ csv_exporter.py
│     │  └─ html_renderer.py
│     ├─ email_service/
│     │  ├─ __init__.py
│     │  └─ smtp_sender.py
│     ├─ scheduler/
│     │  ├─ __init__.py
│     │  └─ daily_scheduler.py
│     ├─ service_runner/
│     │  ├─ __init__.py
│     │  ├─ supervisor.py
│     │  └─ windows_service.py
│     ├─ utils/
│     │  ├─ __init__.py
│     │  ├─ logging_setup.py
│     │  ├─ time_utils.py
│     │  └─ health.py
│     └─ templates/
│        └─ daily_report.html.j2
└─ tests/
   ├─ unit/
   ├─ integration/
   └─ fixtures/
```

### Development Mode vs Production Mode (planned)
- **Development mode**
  - Console logging enabled.
  - Email directed to test recipient and/or dry-run sink.
  - Simulated event injector for validation.
- **Production mode**
  - Windows service/task scheduler startup.
  - Full encrypted storage and scheduled send at 18:00.
  - Strict error handling and health metrics.

