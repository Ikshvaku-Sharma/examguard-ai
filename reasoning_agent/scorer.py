"""
Integrity Scorer
─────────────────
Rule-based scoring engine that updates the Integrity Score
fast (no LLM call) on every incoming anomaly event.

Score starts at 100 and decreases based on event type and severity.
Score recovers slowly over time without anomalies (not implemented here —
recovery is handled by a periodic background task in the backend).
"""

from dataclasses import dataclass


# Score deduction per event type and severity
_DEDUCTIONS = {
    "face_absent":    {"LOW": 5,  "MEDIUM": 12, "HIGH": 20},
    "multiple_faces": {"LOW": 10, "MEDIUM": 20, "HIGH": 30},
    "gaze_deviation": {"LOW": 2,  "MEDIUM": 5,  "HIGH": 10},
    "phone_detected": {"LOW": 10, "MEDIUM": 20, "HIGH": 35},
    "tab_switch":     {"LOW": 3,  "MEDIUM": 6,  "HIGH": 10},
}

_DEFAULT_DEDUCTION = 5   # for unknown event types


class IntegrityScorer:
    """
    Stateless scorer — the caller passes in the current score and
    receives the updated score back.
    """

    def update(self, current_score: int, event: dict) -> int:
        event_type = event.get("event_type", "unknown")
        severity   = event.get("severity", "MEDIUM")
        confidence = float(event.get("confidence", 1.0))

        base_deduction = (
            _DEDUCTIONS
            .get(event_type, {})
            .get(severity, _DEFAULT_DEDUCTION)
        )

        # Scale deduction by detection confidence (less confident = smaller penalty)
        actual_deduction = round(base_deduction * confidence)

        new_score = max(0, current_score - actual_deduction)
        return new_score

    def verdict(self, score: int) -> str:
        if score >= 75:
            return "CLEAR"
        elif score >= 50:
            return "SUSPICIOUS"
        else:
            return "COMPROMISED"
