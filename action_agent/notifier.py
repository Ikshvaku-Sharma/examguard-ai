"""
Email / Webhook Notifier
─────────────────────────
Sends admin alerts via SMTP email when an incident is detected.
Also supports a generic webhook POST for Slack / Teams / custom integrations.
"""

import json
import logging
import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

import httpx

log = logging.getLogger(__name__)

SMTP_HOST    = os.getenv("SMTP_HOST",   "smtp.gmail.com")
SMTP_PORT    = int(os.getenv("SMTP_PORT", 587))
SMTP_USER    = os.getenv("SMTP_USER",   "")
SMTP_PASS    = os.getenv("SMTP_PASS",   "")
ADMIN_EMAIL  = os.getenv("ADMIN_EMAIL", "")
WEBHOOK_URL  = os.getenv("WEBHOOK_URL", "")   # optional Slack/Teams webhook


_VERDICT_EMOJI = {
    "CLEAR":       "✅",
    "SUSPICIOUS":  "⚠️",
    "COMPROMISED": "🚨",
}


def send_email_alert(alert: dict) -> bool:
    """
    Send an HTML email alert to the admin.
    Returns True on success, False on failure.
    Silently skips if SMTP credentials are not configured.
    """
    if not all([SMTP_USER, SMTP_PASS, ADMIN_EMAIL]):
        log.info("SMTP not configured — skipping email alert")
        return False

    sid       = alert.get("session_id",      "unknown")
    score     = alert.get("integrity_score", 0)
    verdict   = alert.get("verdict",         "SUSPICIOUS")
    reasoning = alert.get("reasoning",       "No details available.")
    ts        = alert.get("timestamp",       datetime.utcnow().isoformat())
    emoji     = _VERDICT_EMOJI.get(verdict, "⚠️")

    subject = f"{emoji} ExamGuard Alert — Session {sid} | {verdict} ({score}/100)"

    html_body = f"""
    <html><body style="font-family:Arial,sans-serif;background:#f4f7fb;padding:20px">
      <div style="max-width:600px;margin:auto;background:#fff;border-radius:10px;
                  border-top:5px solid #00C6FF;padding:30px">
        <h2 style="color:#0D1B3E;margin-top:0">ExamGuard AI — Incident Alert</h2>
        <table style="width:100%;border-collapse:collapse;margin-bottom:20px">
          <tr><td style="padding:8px;background:#eef3fa;font-weight:bold;width:40%">Session ID</td>
              <td style="padding:8px">{sid}</td></tr>
          <tr><td style="padding:8px;font-weight:bold">Timestamp (UTC)</td>
              <td style="padding:8px">{ts}</td></tr>
          <tr><td style="padding:8px;background:#eef3fa;font-weight:bold">Integrity Score</td>
              <td style="padding:8px"><strong>{score}/100</strong></td></tr>
          <tr><td style="padding:8px;font-weight:bold">Verdict</td>
              <td style="padding:8px">
                <span style="font-size:18px;font-weight:bold;
                  color:{'#EF4444' if verdict=='COMPROMISED' else '#F59E0B' if verdict=='SUSPICIOUS' else '#10B981'}">
                  {emoji} {verdict}
                </span>
              </td></tr>
        </table>
        <h3 style="color:#1A3A6B">AI Reasoning</h3>
        <p style="background:#f8fafc;padding:15px;border-radius:6px;
                  border-left:4px solid #00C6FF;margin:0">{reasoning}</p>
        <p style="margin-top:24px;font-size:12px;color:#94a3b8">
          This alert was generated autonomously by ExamGuard AI.
          Log in to the dashboard to review the full incident report.
        </p>
      </div>
    </body></html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = SMTP_USER
    msg["To"]      = ADMIN_EMAIL
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, ADMIN_EMAIL, msg.as_string())
        log.info("Email alert sent to %s", ADMIN_EMAIL)
        return True
    except Exception as exc:
        log.error("Failed to send email: %s", exc)
        return False


def send_webhook_alert(alert: dict) -> bool:
    """
    POST a JSON payload to a configured webhook URL (Slack / Teams / custom).
    Silently skips if WEBHOOK_URL is not set.
    """
    if not WEBHOOK_URL:
        return False

    sid     = alert.get("session_id",      "unknown")
    score   = alert.get("integrity_score", 0)
    verdict = alert.get("verdict",         "SUSPICIOUS")
    emoji   = _VERDICT_EMOJI.get(verdict, "⚠️")

    # Slack-compatible payload
    payload = {
        "text": f"{emoji} *ExamGuard Alert* — Session `{sid}`",
        "attachments": [{
            "color":  "#EF4444" if verdict == "COMPROMISED" else "#F59E0B",
            "fields": [
                {"title": "Verdict",         "value": verdict,          "short": True},
                {"title": "Integrity Score", "value": f"{score}/100",   "short": True},
                {"title": "Reasoning",       "value": alert.get("reasoning", ""), "short": False},
            ],
        }],
    }

    try:
        resp = httpx.post(WEBHOOK_URL, json=payload, timeout=5.0)
        resp.raise_for_status()
        log.info("Webhook alert sent to %s", WEBHOOK_URL)
        return True
    except Exception as exc:
        log.error("Webhook failed: %s", exc)
        return False
