"""
Gaze Detector
─────────────
Estimates gaze direction from MediaPipe FaceMesh landmarks.
Returns whether gaze is deviated from the screen and by how much.

Technique: Uses iris landmarks (added in MediaPipe 0.8.9 with refine_landmarks=True)
to compute the iris centre position relative to the eye corners, which gives
a reliable left/right/up/down deviation estimate without a dedicated iris model.
"""

import os
from dataclasses import dataclass
from typing import Any, Optional

import numpy as np


# Sensitivity: fraction of eye-width the iris can shift before flagging.
# Lower = more sensitive. Tune via GAZE_SENSITIVITY env var.
_SENSITIVITY = float(os.getenv("GAZE_SENSITIVITY", 0.30))

# MediaPipe FaceMesh landmark indices
_LEFT_EYE_INNER   = 133
_LEFT_EYE_OUTER   = 33
_LEFT_IRIS_CENTER = 468          # available only with refine_landmarks=True

_RIGHT_EYE_INNER   = 362
_RIGHT_EYE_OUTER   = 263
_RIGHT_IRIS_CENTER = 473

_UPPER_LIP = 13
_LOWER_LIP = 14


@dataclass
class GazeResult:
    is_deviated:     bool
    direction:       str     # "left" | "right" | "up" | "down" | "center"
    deviation_angle: float   # approximate degrees
    confidence:      float


class GazeDetector:

    def analyze(self, frame, landmarks) -> GazeResult:
        """
        Compute gaze deviation from face mesh landmarks.
        Returns a GazeResult. If landmarks are None, returns a safe default.
        """
        if landmarks is None:
            return GazeResult(is_deviated=False, direction="center",
                              deviation_angle=0.0, confidence=0.0)

        h, w = frame.shape[:2]
        pts  = landmarks.landmark

        def to_px(idx):
            lm = pts[idx]
            return np.array([lm.x * w, lm.y * h])

        try:
            # ── Horizontal gaze (iris position within eye) ─────────
            left_inner   = to_px(_LEFT_EYE_INNER)
            left_outer   = to_px(_LEFT_EYE_OUTER)
            left_iris    = to_px(_LEFT_IRIS_CENTER)
            right_inner  = to_px(_RIGHT_EYE_INNER)
            right_outer  = to_px(_RIGHT_EYE_OUTER)
            right_iris   = to_px(_RIGHT_IRIS_CENTER)

            eye_w_left   = np.linalg.norm(left_outer  - left_inner)
            eye_w_right  = np.linalg.norm(right_outer - right_inner)

            # Normalised iris offset: 0 = centre, ±1 = at corner
            left_offset  = (left_iris[0]  - left_inner[0])  / (eye_w_left  + 1e-6) - 0.5
            right_offset = (right_iris[0] - right_inner[0]) / (eye_w_right + 1e-6) - 0.5
            h_offset     = (left_offset + right_offset) / 2.0   # average both eyes

            # ── Approximate deviation angle (very rough) ───────────
            # Each eye spans ~30° of horizontal FOV; sensitivity threshold
            # maps the fraction to degrees.
            angle    = abs(h_offset) / 0.5 * 30.0
            deviated = abs(h_offset) > _SENSITIVITY

            if not deviated:
                direction = "center"
            elif h_offset < 0:
                direction = "left"
            else:
                direction = "right"

            confidence = min(1.0, abs(h_offset) / (_SENSITIVITY + 1e-6))
            return GazeResult(
                is_deviated=deviated,
                direction=direction,
                deviation_angle=angle,
                confidence=confidence,
            )

        except (IndexError, ZeroDivisionError):
            return GazeResult(is_deviated=False, direction="center",
                              deviation_angle=0.0, confidence=0.0)
