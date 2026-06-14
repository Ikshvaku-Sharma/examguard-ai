#!/usr/bin/env python3
"""
ExamGuard AI — Demo Simulation Script
────────────────────────────────────────
Simulates the "student cheats" demo scenario from the pitch deck
by publishing fake anomaly events to Redis at scripted intervals.

Useful for:
  - Testing the Reasoning + Action agents without a real webcam
  - Live demos during hackathon judging

Usage:
    python scripts/simulate_demo.py
"""

import asyncio
import json
import os
import sys
from datetime import datetime

import redis.asyncio as aioredis

REDIS_URL  = os.getenv("REDIS_URL", "redis://localhost:6379")
SESSION_ID = os.getenv("DEMO_SESSION_ID", "demo_session_001")


# Scripted timeline matching the pitch deck demo scenario
SCENARIO = [
    {
        "delay": 0,
        "event_type": "phone_detected",
        "severity": "MEDIUM",
        "confidence": 0.82,
        "description": "Phone or electronic device detected with 82% confidence.",
        "metadata": {"bbox": [120, 340, 220, 460]},
    },
    {
        "delay": 12,
        "event_type": "multiple_faces",
        "severity": "HIGH",
        "confidence": 0.91,
        "description": "Multiple faces detected (2). Possible third-party assistance.",
        "metadata": {"face_count": 2},
    },
    {
        "delay": 13,
        "event_type": "tab_switch",
        "severity": "LOW",
        "confidence": 1.0,
        "description": "Student switched to another window: 'WhatsApp Web'",
        "metadata": {"window_title": "WhatsApp Web"},
    },
    {
        "delay": 8,
        "event_type": "gaze_deviation",
        "severity": "HIGH",
        "confidence": 0.78,
        "description": "Gaze deviated 38.2° from screen center.",
        "metadata": {"angle": 38.2, "direction": "left"},
    },
]


async def main():
    print(f"🛡️  ExamGuard AI — Demo Simulation")
    print(f"Session ID: {SESSION_ID}")
    print(f"Connecting to Redis at {REDIS_URL}...")

    redis = await aioredis.from_url(REDIS_URL, decode_responses=True)
    print("✅ Connected. Starting scenario in 2 seconds...\n")
    await asyncio.sleep(2)

    for i, step in enumerate(SCENARIO, 1):
        await asyncio.sleep(step["delay"])

        event = {
            "session_id":  SESSION_ID,
            "timestamp":   datetime.utcnow().isoformat(),
            "event_type":  step["event_type"],
            "severity":    step["severity"],
            "confidence":  step["confidence"],
            "description": step["description"],
            "frame_b64":   None,
            "metadata":    step["metadata"],
        }

        await redis.publish("anomalies", json.dumps(event))
        print(f"[{i}/{len(SCENARIO)}] Published: {step['event_type']} ({step['severity']}) — {step['description']}")

    print("\n✅ Scenario complete. Check the dashboard for the autonomous response!")
    await redis.aclose()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
