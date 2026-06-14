<div align="center">

# 🛡️ ExamGuard AI

### Autonomous Exam Integrity Monitor

**FAR AWAY 2026 — India's Biggest International Hackathon**

[![Theme](https://img.shields.io/badge/Theme-Agentic%20%26%20Autonomous%20Systems-00C6FF?style=for-the-badge)](https://github.com)
[![Theme](https://img.shields.io/badge/Theme-Examinations-1A3A6B?style=for-the-badge)](https://github.com)
[![Stack](https://img.shields.io/badge/Stack-Python%20%7C%20FastAPI%20%7C%20React-white?style=for-the-badge)](https://github.com)

*A fully autonomous multi-agent system that monitors, analyzes, scores, reports,*
*and acts on exam malpractice — with zero human intervention.*

</div>

---

## 🎯 Problem

- **51%** of Indian students admit to cheating in exams
- **₹2B+** lost annually to exam fraud
- **0** fully autonomous proctoring solutions exist today

Human proctors are expensive and don't scale. Existing AI tools only *flag* anomalies — they never *decide* or *act* autonomously. No system connects webcam detection → behavioral scoring → instant report → alert in one closed loop.

---

## 💡 Solution

ExamGuard AI is a **5-stage autonomous agent pipeline**:

```
Webcam/Screen  →  Vision Agent  →  Reasoning Agent  →  Action Agent  →  Audit Store
                  (detects)        (LLM scores)        (acts + alerts)   (logs everything)
```

Every stage runs without any human in the loop.

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         ExamGuard AI Pipeline                            │
│                                                                          │
│  ┌─────────┐   ┌────────────┐   ┌─────────────────┐   ┌─────────────┐  │
│  │  INPUT  │──▶│   VISION   │──▶│   REASONING     │──▶│   ACTION   │  │
│  │  LAYER  │   │   AGENT    │   │   AGENT (LLM)   │   │   AGENT    │  │
│  │         │   │            │   │                 │   │            │  │
│  │ Webcam  │   │ OpenCV     │   │ LangChain       │   │ PDF Report │  │
│  │ Screen  │   │ MediaPipe  │   │ GPT-4 / Llama3  │   │ Email Alert│  │
│  │ Mic     │   │ YOLO v8    │   │ Integrity Score │   │ Dashboard  │  │
│  └─────────┘   └─────┬──────┘   └───────┬─────────┘   └─────┬─────┘  │
│                       │ Redis             │ Redis              │ REST   │
│                   'anomalies'          'alerts'           Backend API   │
│                                                                          │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  FastAPI Backend  ←→  PostgreSQL  ←→  React Dashboard (WebSocket) │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Quick Start (2 commands)

```bash
# 1. Clone and configure
git clone https://github.com/YOUR_USERNAME/examguard-ai.git
cd examguard-ai
cp .env.example .env
# → Edit .env: set OPENAI_API_KEY or GROQ_API_KEY (free at console.groq.com)

# 2. Launch everything
docker-compose up --build
```

**That's it.** Services start at:

| Service | URL |
|---------|-----|
| 🖥️ Dashboard | http://localhost:3000 |
| 🔌 API | http://localhost:8000 |
| 📖 API Docs | http://localhost:8000/docs |

---

## 🎬 Run the Demo (no webcam needed)

After `docker-compose up`, in a new terminal:

```bash
docker-compose --profile demo up demo_simulator
```

This replays the exact demo scenario: phone detected → second face → tab switch → score drops → **autonomous incident report generated in < 2 seconds**. Watch it live on the dashboard.

Or manually:
```bash
cd scripts
pip install redis
python simulate_demo.py
```

---

## 📁 Project Structure

```
examguard-ai/
│
├── vision_agent/              # 🎥 Stage 1 — Computer vision pipeline
│   ├── agent.py               #    Main loop: captures frames, fires detectors
│   ├── detectors/
│   │   ├── face.py            #    MediaPipe — face count & landmarks
│   │   ├── gaze.py            #    Iris landmark gaze deviation (±angle, direction)
│   │   ├── phone.py           #    YOLOv8n — phone & forbidden object detection
│   │   └── screen.py          #    Active window / tab-switch monitoring
│   ├── requirements.txt
│   └── Dockerfile
│
├── reasoning_agent/           # 🧠 Stage 2 — LLM-powered scoring
│   ├── agent.py               #    Subscribes to anomalies, runs LLM chain
│   ├── scorer.py              #    Fast rule-based integrity score (0–100)
│   ├── prompts.py             #    System prompt + context builder
│   ├── requirements.txt
│   └── Dockerfile
│
├── action_agent/              # ⚡ Stage 3 — Autonomous response
│   ├── agent.py               #    Subscribes to alerts, runs 3 actions in parallel
│   ├── report_gen.py          #    ReportLab PDF incident report generator
│   ├── notifier.py            #    SMTP email + Slack/webhook alerts
│   ├── requirements.txt
│   └── Dockerfile
│
├── backend/                   # 🔌 FastAPI REST + WebSocket server
│   ├── main.py                #    App entry, Redis→WebSocket bridge
│   ├── routers/
│   │   ├── sessions.py        #    CRUD for exam sessions
│   │   ├── incidents.py       #    Incident log CRUD
│   │   ├── reports.py         #    PDF upload/download
│   │   └── stats.py           #    Dashboard aggregate stats
│   ├── db/
│   │   ├── database.py        #    SQLAlchemy async engine
│   │   ├── models.py          #    ORM models (Session, Incident, AuditEvent)
│   │   └── init.sql           #    Postgres init + demo seed data
│   ├── models/schemas.py      #    Pydantic request/response schemas
│   ├── requirements.txt
│   └── Dockerfile
│
├── dashboard/                 # 🖥️ React admin dashboard
│   ├── src/
│   │   ├── App.tsx            #    Root with sidebar routing
│   │   ├── api.ts             #    Axios client + TypeScript types
│   │   ├── pages/
│   │   │   ├── Overview.tsx   #    Live stats + real-time score chart
│   │   │   ├── Sessions.tsx   #    All exam sessions table
│   │   │   └── Incidents.tsx  #    Incident log with AI reasoning + PDF links
│   │   ├── components/
│   │   │   ├── StatCard.tsx
│   │   │   ├── VerdictBadge.tsx
│   │   │   └── LiveAlertToast.tsx  # Real-time popup alerts
│   │   └── hooks/
│   │       └── useLiveFeed.ts      # WebSocket hook with auto-reconnect
│   ├── package.json
│   └── Dockerfile
│
├── tests/                     # ✅ Unit + integration tests
│   ├── test_scorer.py
│   └── test_incidents_api.py
│
├── scripts/
│   ├── simulate_demo.py       # 🎬 Demo scenario simulator
│   ├── setup.sh               # One-command dev setup
│   └── Dockerfile.simulator
│
├── docs/ARCHITECTURE.md       # Deep-dive architecture doc
├── docker-compose.yml         # Full stack orchestration
├── .env.example               # Environment template
└── README.md
```

---

## 🔑 Key Features

| Feature | Detail |
|---------|--------|
| **Multi-modal detection** | Webcam + screen + audio + keyboard — 4 input streams simultaneously |
| **LLM reasoning core** | GPT-4 / Llama 3 reasons about context, not just individual events |
| **Zero human intervention** | Full loop: detect → score → decide → report → alert, no human needed |
| **Explainable verdicts** | Every flag: *"Student looked left 11× in 4 min. Confidence: 87%"* |
| **Real-time dashboard** | WebSocket-driven, live integrity score chart, instant alert toasts |
| **Privacy-first** | All processing on-premise / private Docker network. No raw video leaves. |
| **One-command deploy** | `docker-compose up --build` — everything containerised |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Vision | Python 3.11, OpenCV, MediaPipe, YOLOv8 |
| Agent Orchestration | LangChain, async Python |
| LLM | OpenAI GPT-4o-mini / Groq Llama 3 (free) |
| Message Bus | Redis Pub/Sub |
| Backend | FastAPI, SQLAlchemy (async), asyncpg |
| Database | PostgreSQL 16 |
| Report Generation | ReportLab |
| Frontend | React 18, TypeScript, Tailwind CSS, Recharts |
| Real-time | WebSockets |
| Infrastructure | Docker Compose |

---

## 📊 Demo Scenario (from pitch deck)

| Time | Event | Agent Response | Severity |
|------|-------|---------------|----------|
| T+0s | Student opens phone | Object detected + downward gaze | MEDIUM |
| T+12s | Second face on webcam | Face count > 1 anomaly | HIGH |
| T+25s | Tab switch to browser | Screen agent detects window change | LOW |
| T+40s | Score drops to 34/100 | Reasoning agent: COMPROMISED | 🚨 ALERT |
| T+41s | Auto-report generated | PDF + email + dashboard push | ACTION |

---

## 👥 Team

**Team ExamGuard** — B.Tech CSE, CGC College of Engineering, Landran

---

## 📄 License

MIT © 2026 Team ExamGuard
