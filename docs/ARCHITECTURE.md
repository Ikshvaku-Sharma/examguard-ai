# ExamGuard AI — Architecture Documentation

## Overview

ExamGuard AI is a five-stage autonomous pipeline. Each stage runs as an
independent service communicating via Redis pub/sub, making the system
horizontally scalable and loosely coupled.

```
┌─────────────┐    ┌──────────────┐    ┌─────────────────┐    ┌──────────────┐    ┌─────────────┐
│ INPUT LAYER │───▶│ VISION AGENT │───▶│ REASONING AGENT │───▶│ ACTION AGENT │───▶│ AUDIT STORE │
└─────────────┘    └──────────────┘    └─────────────────┘    └──────────────┘    └─────────────┘
                    publishes to              publishes to          publishes to
                    'anomalies'               'alerts' &            backend REST API
                                               'reasoning_results'
```

## Component Details

### 1. Vision Agent (`vision_agent/`)

Runs at `CAPTURE_FPS` (default 5fps). Each frame is passed through four detectors:

| Detector | Library | Detects |
|----------|---------|---------|
| `FaceDetector` | MediaPipe Face Detection + Face Mesh | Face count, landmarks |
| `GazeDetector` | MediaPipe iris landmarks | Gaze deviation angle & direction |
| `PhoneDetector` | YOLOv8n | Phones, books, other forbidden objects |
| `ScreenDetector` | pygetwindow | Active window / tab switches |

Each detector returns a result object. If an anomaly is found, an `AnomalyEvent`
is constructed and published to the Redis channel `anomalies`.

### 2. Reasoning Agent (`reasoning_agent/`)

Subscribes to `anomalies`. Maintains a sliding window (last 20 events) per session.

**Two-tier scoring:**
1. **Fast path** (`scorer.py`) — rule-based deduction table, runs on every event,
   no LLM call. Updates `integrity_score` immediately.
2. **Deep path** (LLM via LangChain) — triggered when score drops below
   `INTEGRITY_THRESHOLD` or a HIGH severity event occurs. The LLM receives the
   recent event context and current score, and returns a structured JSON verdict:
   ```json
   {
     "integrity_score": 34,
     "verdict": "COMPROMISED",
     "reasoning": "...",
     "triggered_by": ["phone_detected", "multiple_faces"]
   }
   ```

If `should_alert` is true, the result is published to `alerts`.

### 3. Action Agent (`action_agent/`)

Subscribes to `alerts`. On each alert, runs three actions concurrently:

1. **`report_gen.py`** — generates a branded PDF incident report (ReportLab)
2. **`notifier.py`** — sends an HTML email to the admin (and optional Slack webhook)
3. **Backend update** — POSTs the incident to `/api/v1/incidents`, which also
   updates the session's `integrity_score` and `verdict`, and uploads the PDF
   via `/api/v1/reports/upload`

### 4. Backend (`backend/`)

FastAPI server. Responsibilities:

- **REST API** — sessions, incidents, reports, stats (see `/docs` for OpenAPI spec)
- **Database** — PostgreSQL via SQLAlchemy async ORM (`db/models.py`)
- **WebSocket bridge** — subscribes to all three Redis channels and forwards
  messages to connected dashboard clients in real-time

### 5. Dashboard (`dashboard/`)

React + TypeScript + Tailwind. Three pages:

- **Overview** — live stat cards + real-time integrity score chart (WebSocket-driven)
- **Sessions** — table of all exam sessions with current scores/verdicts
- **Incidents** — feed of AI-generated incident reports with reasoning trace
  and PDF download links

---

## Data Flow Example

1. Webcam frame shows a second face → `FaceDetector` flags `multiple_faces` (HIGH)
2. `AnomalyEvent` published to `anomalies`
3. Reasoning Agent: fast-path scorer drops score 100 → 70
4. HIGH severity triggers LLM deep reasoning
5. LLM returns `{"integrity_score": 65, "verdict": "SUSPICIOUS", ...}`
6. Score still above threshold (50) → no alert yet, but result published to
   `reasoning_results` → dashboard chart updates live
7. (Later) Phone also detected → score drops to 34 → `should_alert=True`
8. Published to `alerts`
9. Action Agent: generates PDF, emails admin, POSTs incident to backend
10. Backend: saves to DB, broadcasts to WebSocket clients
11. Dashboard: incident appears instantly in Incidents tab with download link

---

## Scaling Considerations

- Each Vision Agent instance handles **one exam session**. For N concurrent
  exams, run N Vision Agent containers (or one process per session with
  session-specific camera devices).
- Reasoning and Action agents are **stateless per-message** (session context
  is held in-memory per agent instance) — can be sharded by session_id hash
  across multiple instances using Redis consumer groups for true horizontal scale.
- PostgreSQL + MinIO can be swapped for managed cloud equivalents
  (RDS, S3) for production deployments.
