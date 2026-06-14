"""
Face Detector
─────────────
Uses MediaPipe Face Detection to count faces in a frame
and extract facial landmarks for downstream gaze analysis.
"""

from dataclasses import dataclass, field
from typing import Any, List, Optional

import cv2
import mediapipe as mp
import numpy as np


@dataclass
class FaceResult:
    face_count: int
    confidence: float
    landmarks:  Optional[Any]   = None    # MediaPipe face mesh landmarks
    bboxes:     List[tuple]     = field(default_factory=list)


class FaceDetector:
    """
    Wraps MediaPipe FaceDetection (fast, lightweight) for presence/count
    and MediaPipe FaceMesh for landmark extraction used by GazeDetector.
    """

    def __init__(self, min_detection_confidence: float = 0.6):
        self._mp_face_detection = mp.solutions.face_detection
        self._mp_face_mesh      = mp.solutions.face_mesh

        self.face_detection = self._mp_face_detection.FaceDetection(
            model_selection=0,
            min_detection_confidence=min_detection_confidence,
        )
        self.face_mesh = self._mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=4,
            refine_landmarks=True,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=0.5,
        )

    def analyze(self, frame: np.ndarray) -> FaceResult:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # ── Fast face detection (count + bboxes) ──────────────────
        detection_result = self.face_detection.process(rgb)
        faces            = detection_result.detections or []
        face_count       = len(faces)

        bboxes     = []
        confidence = 0.0
        if faces:
            for det in faces:
                score     = det.score[0] if det.score else 0.0
                confidence = max(confidence, score)
                bbc       = det.location_data.relative_bounding_box
                h, w      = frame.shape[:2]
                bboxes.append((
                    int(bbc.xmin * w),
                    int(bbc.ymin * h),
                    int(bbc.width * w),
                    int(bbc.height * h),
                ))

        # ── Face mesh for landmarks (used by GazeDetector) ────────
        landmarks = None
        if face_count == 1:
            mesh_result = self.face_mesh.process(rgb)
            if mesh_result.multi_face_landmarks:
                landmarks = mesh_result.multi_face_landmarks[0]

        return FaceResult(
            face_count=face_count,
            confidence=confidence,
            landmarks=landmarks,
            bboxes=bboxes,
        )
