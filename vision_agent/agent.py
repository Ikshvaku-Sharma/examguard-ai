"""
ExamGuard AI — Vision Agent
────────────────────────────
Continuously captures webcam + screen frames, runs detection pipeline,
and publishes anomaly events to the backend via Redis pub/sub.
"""

import asyncio
import base64
import json
import logging
import os
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Optional

import cv2
import redis.asyncio as aioredis

from detectors.face import FaceDetector
from detectors.gaze import GazeDetector
from detectors.phone import PhoneDetector
from detectors.screen import ScreenDetector

logging.basicConfig(level=logging.INFO, format="%(asctime)s [VISION] %(message)s")
log = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────
CAMERA_INDEX    = int(os.getenv("CAMERA_INDEX", 0))
CAPTURE_FPS     = int(os.getenv("CAPTURE_FPS", 5))
REDIS_URL       = os.getenv("REDIS_URL", "redis://localhost:6379")
SESSION_ID      = os.getenv("SESSION_ID", "default_session")
FRAME_INTERVAL  = 1.0 / CAPTURE_FPS


@dataclass
class AnomalyEvent:
    session_id: str
    timestamp:  str
    event_type: str          # gaze_deviation | face_absent | multiple_faces | phone_detected | tab_switch
    severity:   str          # LOW | MEDIUM | HIGH
    confidence: float        # 0.0 – 1.0
    description: str
    frame_b64:  Optional[str] = None   # base64-encoded JPEG snapshot
    metadata:   dict         = field(default_factory=dict)


class VisionAgent:
    """
    Main vision pipeline. Runs all detectors each frame and
    publishes AnomalyEvent objects to Redis channel 'anomalies'.
    """

    def __init__(self):
        self.cap            = None
        self.redis          = None
        self.face_detector  = FaceDetector()
        self.gaze_detector  = GazeDetector()
        self.phone_detector = PhoneDetector()
        self.screen_monitor = ScreenDetector()
        self.running        = False
        self._frame_count   = 0

    # ── Lifecycle ─────────────────────────────────────────────────

    async def start(self):
        log.info("Starting Vision Agent (camera=%d, fps=%d)", CAMERA_INDEX, CAPTURE_FPS)
        self.redis = await aioredis.from_url(REDIS_URL, decode_responses=True)
        self.cap   = cv2.VideoCapture(CAMERA_INDEX)

        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open camera at index {CAMERA_INDEX}")

        # Set resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        self.running = True
        log.info("Vision Agent ready. Publishing to Redis channel 'anomalies'")
        await self._capture_loop()

    async def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
        if self.redis:
            await self.redis.aclose()
        log.info("Vision Agent stopped.")

    # ── Main loop ─────────────────────────────────────────────────

    async def _capture_loop(self):
        while self.running:
            loop_start = time.monotonic()

            ret, frame = self.cap.read()
            if not ret:
                log.warning("Frame capture failed — retrying")
                await asyncio.sleep(0.1)
                continue

            self._frame_count += 1
            events = await self._run_detectors(frame)

            for event in events:
                await self._publish(event)

            # Throttle to target FPS
            elapsed = time.monotonic() - loop_start
            await asyncio.sleep(max(0.0, FRAME_INTERVAL - elapsed))

    # ── Detector pipeline ─────────────────────────────────────────

    async def _run_detectors(self, frame) -> list[AnomalyEvent]:
        events = []
        ts = datetime.utcnow().isoformat()

        # 1. Face presence & count
        face_result = self.face_detector.analyze(frame)
        if face_result.face_count == 0:
            events.append(AnomalyEvent(
                session_id  = SESSION_ID,
                timestamp   = ts,
                event_type  = "face_absent",
                severity    = "HIGH",
                confidence  = face_result.confidence,
                description = "No face detected in frame. Student may have left the exam.",
                frame_b64   = _encode_frame(frame),
                metadata    = {"face_count": 0},
            ))
        elif face_result.face_count > 1:
            events.append(AnomalyEvent(
                session_id  = SESSION_ID,
                timestamp   = ts,
                event_type  = "multiple_faces",
                severity    = "HIGH",
                confidence  = face_result.confidence,
                description = f"Multiple faces detected ({face_result.face_count}). Possible third-party assistance.",
                frame_b64   = _encode_frame(frame),
                metadata    = {"face_count": face_result.face_count},
            ))

        # 2. Gaze direction (only if exactly one face present)
        if face_result.face_count == 1:
            gaze_result = self.gaze_detector.analyze(frame, face_result.landmarks)
            if gaze_result.is_deviated:
                events.append(AnomalyEvent(
                    session_id  = SESSION_ID,
                    timestamp   = ts,
                    event_type  = "gaze_deviation",
                    severity    = "MEDIUM" if gaze_result.deviation_angle < 30 else "HIGH",
                    confidence  = gaze_result.confidence,
                    description = f"Gaze deviated {gaze_result.deviation_angle:.1f}° from screen center.",
                    frame_b64   = _encode_frame(frame),
                    metadata    = {
                        "angle":     gaze_result.deviation_angle,
                        "direction": gaze_result.direction,
                    },
                ))

        # 3. Phone / foreign object detection
        phone_result = self.phone_detector.analyze(frame)
        if phone_result.detected:
            events.append(AnomalyEvent(
                session_id  = SESSION_ID,
                timestamp   = ts,
                event_type  = "phone_detected",
                severity    = "HIGH",
                confidence  = phone_result.confidence,
                description = f"Phone or electronic device detected with {phone_result.confidence:.0%} confidence.",
                frame_b64   = _encode_frame(frame),
                metadata    = {"bbox": phone_result.bbox},
            ))

        # 4. Screen / tab monitoring
        screen_result = self.screen_monitor.check()
        if screen_result.tab_switched:
            events.append(AnomalyEvent(
                session_id  = SESSION_ID,
                timestamp   = ts,
                event_type  = "tab_switch",
                severity    = "LOW",
                confidence  = 1.0,
                description = f"Student switched to another window: '{screen_result.window_title}'",
                metadata    = {"window_title": screen_result.window_title},
            ))

        return events

    # ── Redis publish ─────────────────────────────────────────────

    async def _publish(self, event: AnomalyEvent):
        payload = json.dumps(asdict(event))
        await self.redis.publish("anomalies", payload)
        log.info("[EVENT] %s | %s | conf=%.2f", event.event_type, event.severity, event.confidence)


# ── Helpers ───────────────────────────────────────────────────────

def _encode_frame(frame) -> str:
    """Encode OpenCV frame to base64 JPEG string."""
    _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
    return base64.b64encode(buf).decode("utf-8")


# ── Entry point ───────────────────────────────────────────────────

if __name__ == "__main__":
    agent = VisionAgent()
    try:
        asyncio.run(agent.start())
    except KeyboardInterrupt:
        asyncio.run(agent.stop())
