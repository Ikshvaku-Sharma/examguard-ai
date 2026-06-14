"""
ExamGuard AI — Action Agent
────────────────────────────
Subscribes to Redis 'alerts' channel.
On each alert it autonomously:
  1. Generates a PDF incident report
  2. Sends email notification to admin
  3. Pushes real-time update to backend dashboard via HTTP
  4. Logs the incident to PostgreSQL via backend API
"""

import asyncio
import json
import logging
import os
from datetime import datetime

import httpx
import redis.asyncio as aioredis

from report_gen import generate_pdf_report
from notifier   import send_email_alert

logging.basicConfig(level=logging.INFO, format="%(asctime)s [ACTION] %(message)s")
log = logging.getLogger(__name__)

REDIS_URL    = os.getenv("REDIS_URL",    "redis://localhost:6379")
BACKEND_URL  = os.getenv("BACKEND_URL",  "http://localhost:8000")


class ActionAgent:

    def __init__(self):
        self.redis  = None
        self.http   = None

    async def start(self):
        log.info("Action Agent starting …")
        self.redis = await aioredis.from_url(REDIS_URL, decode_responses=True)
        self.http  = httpx.AsyncClient(base_url=BACKEND_URL, timeout=10.0)

        pubsub = self.redis.pubsub()
        await pubsub.subscribe("alerts")
        log.info("Subscribed to Redis channel 'alerts'")

        async for message in pubsub.listen():
            if message["type"] != "message":
                continue
            try:
                alert = json.loads(message["data"])
                await self._handle_alert(alert)
            except Exception as exc:
                log.error("Error handling alert: %s", exc)

    async def _handle_alert(self, alert: dict):
        sid   = alert["session_id"]
        score = alert["integrity_score"]
        log.warning("[ALERT] Handling alert for session %s (score=%d)", sid, score)

        # Run all actions concurrently
        results = await asyncio.gather(
            self._generate_report(alert),
            self._notify_admin(alert),
            self._update_backend(alert),
            return_exceptions=True,
        )

        for i, res in enumerate(results):
            if isinstance(res, Exception):
                log.error("Action %d failed: %s", i, res)

    async def _generate_report(self, alert: dict) -> str:
        """Generate PDF incident report and upload to MinIO via backend."""
        report_path = await asyncio.to_thread(generate_pdf_report, alert)
        log.info("[ACTION] PDF report generated: %s", report_path)

        # Upload to backend
        with open(report_path, "rb") as f:
            resp = await self.http.post(
                "/api/v1/reports/upload",
                files={"file": (os.path.basename(report_path), f, "application/pdf")},
                data={"session_id": alert["session_id"]},
            )
            resp.raise_for_status()

        return report_path

    async def _notify_admin(self, alert: dict):
        """Send email notification to administrator."""
        await asyncio.to_thread(send_email_alert, alert)
        log.info("[ACTION] Email notification sent for session %s", alert["session_id"])

    async def _update_backend(self, alert: dict):
        """POST incident to backend so dashboard updates in real-time."""
        resp = await self.http.post("/api/v1/incidents", json={
            "session_id":      alert["session_id"],
            "timestamp":       alert["timestamp"],
            "integrity_score": alert["integrity_score"],
            "verdict":         alert["verdict"],
            "reasoning":       alert["reasoning"],
            "triggered_by":    alert.get("triggered_by", []),
        })
        resp.raise_for_status()
        log.info("[ACTION] Incident logged to backend DB")

    async def stop(self):
        if self.http:
            await self.http.aclose()
        if self.redis:
            await self.redis.aclose()


if __name__ == "__main__":
    agent = ActionAgent()
    try:
        asyncio.run(agent.start())
    except KeyboardInterrupt:
        asyncio.run(agent.stop())
