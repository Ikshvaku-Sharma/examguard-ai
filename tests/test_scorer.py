"""
Unit tests for the Integrity Scorer (reasoning_agent/scorer.py)
Run with: pytest tests/test_scorer.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "reasoning_agent"))

from scorer import IntegrityScorer  # noqa: E402


def test_initial_score_unaffected_by_low_severity():
    scorer = IntegrityScorer()
    event = {"event_type": "gaze_deviation", "severity": "LOW", "confidence": 1.0}
    new_score = scorer.update(current_score=100, event=event)
    assert new_score == 98   # 100 - 2


def test_phone_detection_high_severity_large_deduction():
    scorer = IntegrityScorer()
    event = {"event_type": "phone_detected", "severity": "HIGH", "confidence": 1.0}
    new_score = scorer.update(current_score=100, event=event)
    assert new_score == 65   # 100 - 35


def test_score_never_goes_below_zero():
    scorer = IntegrityScorer()
    event = {"event_type": "multiple_faces", "severity": "HIGH", "confidence": 1.0}
    new_score = scorer.update(current_score=10, event=event)
    assert new_score == 0


def test_confidence_scales_deduction():
    scorer = IntegrityScorer()
    event = {"event_type": "phone_detected", "severity": "HIGH", "confidence": 0.5}
    new_score = scorer.update(current_score=100, event=event)
    # 35 * 0.5 = 17.5 -> round -> 18
    assert new_score == 82


def test_verdict_thresholds():
    scorer = IntegrityScorer()
    assert scorer.verdict(90) == "CLEAR"
    assert scorer.verdict(75) == "CLEAR"
    assert scorer.verdict(60) == "SUSPICIOUS"
    assert scorer.verdict(50) == "SUSPICIOUS"
    assert scorer.verdict(30) == "COMPROMISED"


def test_unknown_event_type_uses_default_deduction():
    scorer = IntegrityScorer()
    event = {"event_type": "unknown_event", "severity": "HIGH", "confidence": 1.0}
    new_score = scorer.update(current_score=100, event=event)
    assert new_score == 95   # default deduction = 5
