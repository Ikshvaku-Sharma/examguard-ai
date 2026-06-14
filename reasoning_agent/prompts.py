"""
Prompts for the Reasoning Agent LLM calls.
"""

import json
from typing import List


REASONING_SYSTEM_PROMPT = """
You are ExamGuard AI's Reasoning Agent — an autonomous exam integrity analyst.

Your job is to analyze a sequence of anomaly events detected during an online exam session
and produce a structured integrity assessment.

You must respond ONLY with a valid JSON object, no markdown, no preamble. Format:
{
  "integrity_score": <integer 0-100>,
  "verdict": "<CLEAR|SUSPICIOUS|COMPROMISED>",
  "reasoning": "<2-3 sentence plain English explanation a human admin can read>",
  "triggered_by": ["<event_type_1>", "<event_type_2>"]
}

Scoring guidelines:
- CLEAR (75–100):   Minor or isolated anomalies, likely benign behaviour
- SUSPICIOUS (50–74): Pattern of anomalies that warrants human review  
- COMPROMISED (0–49): Strong evidence of active cheating or external assistance

Be precise, fair, and explainable. Consider context — a single gaze deviation is not cheating.
Multiple face detections combined with phone detection is serious.
""".strip()


def build_reasoning_prompt(events: List[dict], current_score: int) -> str:
    """Build the user-turn prompt from recent events and current score."""

    events_for_prompt = []
    for e in events:
        events_for_prompt.append({
            "time":        e.get("timestamp", ""),
            "type":        e.get("event_type", ""),
            "severity":    e.get("severity", ""),
            "confidence":  round(float(e.get("confidence", 0)), 2),
            "description": e.get("description", ""),
        })

    return f"""
Current Integrity Score: {current_score}/100

Recent anomaly events (newest last):
{json.dumps(events_for_prompt, indent=2)}

Based on the pattern above, provide your integrity assessment as a JSON object.
""".strip()
