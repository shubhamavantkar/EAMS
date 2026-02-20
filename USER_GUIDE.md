# EAMS User Guide

This guide explains how to configure, run, and verify the **Employee Activity Monitoring System (EAMS)** on a Windows endpoint.

## 1) What EAMS does

EAMS is a local endpoint agent that:
- tracks active vs idle time,
- records foreground app usage durations,
- extracts browser domain activity from active window metadata,
- writes encrypted local event logs,
- generates a daily CSV + HTML report,
- emails the report at a configured hour (default: 18:00 local time).

> EAMS does **not** capture keystrokes, passwords, clipboard, file contents, or message content.

## 2) System requirements

- **OS:** Windows (recommended, because foreground/system event collection uses Windows APIs).
- **Python:** 3.11+
- **Network:** outbound SMTP access to your mail server.

## 3) Project setup

From the project root:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 4) Configure environment variables

1. Copy the sample environment file:

```bash
copy .env.example .env
```

2. Edit `.env` and set all required values.

### Required settings

| Variable | Description | Example |
|---|---|---|
| `EAMS_RECIPIENT_EMAIL` | Email that receives daily reports | `ops@example.com` |
| `EAMS_SMTP_HOST` | SMTP hostname | `smtp.gmail.com` |
| `EAMS_SMTP_PORT` | SMTP port | `587` |
| `EAMS_SMTP_USERNAME` | SMTP login username | `monitor@example.com` |
| `EAMS_SMTP_PASSWORD` | SMTP password / app password | `********` |
| `EAMS_STORAGE_KEY` | Fernet key used to encrypt local event logs | generated key |

### Common optional settings

| Variable | Default | Notes |
|---|---:|---|
| `EAMS_MODE` | `development` | Runtime mode label in logs |
| `EAMS_ENDPOINT_ID` | `endpoint-001` | Included in report subject/body |
| `EAMS_DATA_DIR` | `./data` | Where encrypted events and reports are stored |
| `EAMS_REPORT_HOUR` | `18` | 24-hour local time for daily report send |
| `EAMS_IDLE_THRESHOLD_SECONDS` | `300` | Seconds of inactivity before idle state |
| `EAMS_POLL_SECONDS` | `5` | Collector polling interval |

### Generate a storage key

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Paste the output into `EAMS_STORAGE_KEY`.

## 5) Run EAMS manually

From project root:

```bash
set PYTHONPATH=src
python -m eams.main
```

What happens when it starts:
- collector and storage threads begin,
- a daily scheduler job is registered at `EAMS_REPORT_HOUR`,
- encrypted events are written under `EAMS_DATA_DIR/events`.

Stop with `Ctrl+C` in console mode.

## 6) Verify it is working

After a short runtime, check:

1. Console logs show startup messages.
2. Event files appear under:
   - `data/events/*.jsonl.enc` (or your custom `EAMS_DATA_DIR`).
3. At report hour (or after enough collected data), report CSV appears:
   - `data/reports/report-YYYY-MM-DD.csv`.
4. Recipient mailbox receives the report email with CSV attachment.

## 7) Run on Windows startup

### Option A: Scheduled Task (recommended in repo)

PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_startup_task.ps1
```

To remove:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\uninstall_service.ps1
```

### Option B: Windows Service

The provided `install_service.ps1` currently prints guidance to install via NSSM/Task Scheduler for MVP.

## 8) Daily operations

- Keep `.env` secure.
- Rotate SMTP credentials as needed.
- Ensure endpoint clock/timezone is correct (scheduling uses local time).
- Periodically review report output in `data/reports`.

## 9) Troubleshooting

### App exits immediately on startup
- Check `.env` for missing required values (`recipient_email`, SMTP fields, `storage_key`).
- Ensure venv is active and dependencies installed.

### No report email received
- Verify SMTP host/port/username/password.
- Confirm sender account is allowed to send SMTP mail (app password, relay policy, etc.).
- Check local report CSV generation in `data/reports` to separate "generation" vs "delivery" issues.

### No browser domain activity
- Domain tracking depends on detected foreground app + window title parsing.
- Non-browser apps or unsupported title formats may produce fewer domain events.

### Permission issues with startup/task
- Run PowerShell as Administrator when required by your endpoint policy.
- Confirm execution policy allows running local scripts (or use `-ExecutionPolicy Bypass` per command above).
