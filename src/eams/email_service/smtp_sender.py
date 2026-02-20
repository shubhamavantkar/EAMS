from __future__ import annotations

import logging
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path

from tenacity import retry, stop_after_attempt, wait_exponential

from eams.models.results import SendResult

LOGGER = logging.getLogger("eams.smtp_sender")


class SMTPSender:
    def __init__(self, host: str, port: int, username: str, password: str, use_tls: bool = True) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), reraise=True)
    def _send(self, message: EmailMessage) -> None:
        context = ssl.create_default_context()
        with smtplib.SMTP(self.host, self.port, timeout=30) as smtp:
            if self.use_tls:
                smtp.starttls(context=context)
            smtp.login(self.username, self.password)
            smtp.send_message(message)

    def send_daily_report(self, recipient: str, subject: str, html_body: str, csv_path: Path) -> SendResult:
        msg = EmailMessage()
        msg["From"] = self.username
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.set_content("Daily report attached. HTML-capable client recommended.")
        msg.add_alternative(html_body, subtype="html")
        msg.add_attachment(csv_path.read_bytes(), maintype="text", subtype="csv", filename=csv_path.name)

        try:
            self._send(msg)
            return SendResult(success=True, attempts=3)
        except Exception as exc:
            LOGGER.exception("Failed sending report email")
            return SendResult(success=False, attempts=3, error_message=str(exc))
