# Employee Activity Monitoring System (EAMS)

Production-oriented Python endpoint agent for work-safe activity monitoring on Windows.

## Features
- Monitors active/idle state (no keystroke capture).
- Tracks foreground application usage durations.
- Captures browser domain-level activity from active window metadata.
- Stores encrypted local logs with integrity checks and rotation.
- Generates daily HTML + CSV report.
- Sends automated report via SMTP at 6:00 PM local time.

## Ethical Boundaries
EAMS does **not** collect passwords, keystrokes, clipboard, personal chat/email content, or file contents.

## Setup
1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and set values, especially SMTP credentials and storage key.
3. Generate a Fernet key if needed:
   ```bash
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```
4. Run in development mode:
   ```bash
   PYTHONPATH=src python -m eams.main
   ```

## Windows Auto-Start
### Option A: Scheduled Task
Use `scripts/setup_startup_task.ps1` to register a startup task.

### Option B: Windows Service
Use `scripts/install_service.ps1` to install as a Windows service (requires admin).

## Deployment Notes
- Keep `.env` secured and never commit credentials.
- Ensure clock/timezone are correct for 6:00 PM scheduling.
- Review log rotation settings in `configs/default.yaml`.
