"""Notification dispatch — pluggable channels (console default, email optional).

Keeps the same shape as connectors/analyzers: one function the rest of the app
calls, channel selected by config. Push (Firebase/OneSignal) slots in here later.
"""
from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from ..core.config import settings

logger = logging.getLogger("noyou.notify")


def _send_console(to: str, subject: str, body: str) -> bool:
    logger.info("NOTIFY [%s] -> %s | %s", settings.project_name, to, subject)
    logger.info("        %s", body)
    return True


def _send_email(to: str, subject: str, body: str) -> bool:
    if not settings.smtp_host:
        return _send_console(to, subject, body)
    try:
        msg = EmailMessage()
        msg["From"] = settings.smtp_from
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
            server.starttls()
            if settings.smtp_user:
                server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
        return True
    except Exception as exc:  # never let a notification failure break a scan
        logger.warning("Email notification failed: %s", exc)
        return False


def _send_resend(to: str, subject: str, body: str) -> bool:
    """Send via Resend's HTTP API (https://resend.com) — the easiest production email."""
    if not settings.resend_api_key:
        return _send_console(to, subject, body)
    try:
        import httpx

        resp = httpx.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {settings.resend_api_key}"},
            json={"from": settings.smtp_from, "to": [to], "subject": subject, "text": body},
            timeout=15,
        )
        resp.raise_for_status()
        return True
    except Exception as exc:  # never let a notification failure break a scan
        logger.warning("Resend notification failed: %s", exc)
        return False


def dispatch_alert(to_email: str, subject: str, body: str) -> bool:
    channel = settings.notify_channel
    if channel == "resend":
        return _send_resend(to_email, subject, body)
    if channel == "email":
        return _send_email(to_email, subject, body)
    return _send_console(to_email, subject, body)
