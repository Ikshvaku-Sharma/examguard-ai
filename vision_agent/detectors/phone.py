"""
Phone Detector
──────────────
Uses YOLO v8 (ultralytics) to detect phones and other
forbidden objects in the webcam frame.
"""

import os
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import numpy as np

_CONFIDENCE_THRESHOLD = float(os.getenv("PHONE_CONFIDENCE", 0.50))

# COCO class IDs for objects that should not appear during exams
_FORBIDDEN_CLASSES = {
    67: "cell phone",
    73: "book",        # closed-book exam
    76: "scissors",    # not forbidden but demonstrates extensibility
}


@dataclass
class PhoneResult:
    detected:   bool
    confidence: float
    label:      str              = ""
    bbox:       Optional[Tuple]  = None    # (x1, y1, x2, y2) in pixels


class PhoneDetector:
    """
    Lazy-loads YOLOv8n (nano — fast, ~6 MB) on first use.
    Falls back gracefully if ultralytics is not installed.
    """

    def __init__(self):
        self._model   = None
        self._enabled = True
        self._load_model()

    def _load_model(self):
        try:
            from ultralytics import YOLO
            self._model = YOLO("yolov8n.pt")   # auto-downloads on first run
        except ImportError:
            self._enabled = False
            import logging
            logging.getLogger(__name__).warning(
                "ultralytics not installed — phone detection disabled. "
                "Run: pip install ultralytics"
            )

    def analyze(self, frame: np.ndarray) -> PhoneResult:
        if not self._enabled or self._model is None:
            return PhoneResult(detected=False, confidence=0.0)

        results = self._model(frame, verbose=False)[0]
        best_conf  = 0.0
        best_label = ""
        best_bbox  = None

        for box in results.boxes:
            cls_id = int(box.cls[0])
            conf   = float(box.conf[0])
            if cls_id in _FORBIDDEN_CLASSES and conf >= _CONFIDENCE_THRESHOLD:
                if conf > best_conf:
                    best_conf  = conf
                    best_label = _FORBIDDEN_CLASSES[cls_id]
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    best_bbox  = (int(x1), int(y1), int(x2), int(y2))

        return PhoneResult(
            detected   = best_conf >= _CONFIDENCE_THRESHOLD,
            confidence = best_conf,
            label      = best_label,
            bbox       = best_bbox,
        )
