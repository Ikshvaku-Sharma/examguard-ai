# FAR AWAY 2026 — Submission Checklist

## Team: ExamGuard
## Project: ExamGuard AI — Autonomous Exam Integrity Monitor
## Theme: Agentic & Autonomous Systems + Examinations

---

## ✅ Submission Requirements

### Mandatory
- [x] **GitHub Repository** — this repo (full source code)
- [x] **Presentation** — ExamGuard_AI_FAR_AWAY_2026.pptx (13 slides)

### Presentation Structure (per FAR AWAY guidelines)
- [x] Problem Statement (Slide 2)
- [x] Solution Overview (Slide 3)
- [x] System Architecture (Slide 4)
- [x] Key Features (Slide 5)
- [x] Agent Workflow (Slide 6)
- [x] Demo Scenario (Slide 7)
- [x] Real-World Impact (Slide 8)
- [x] Tech Stack (Slide 9)
- [x] Innovation & Differentiation (Slide 10)
- [x] Future Scope (Slide 11)
- [x] Team & GitHub (Slide 12)

---

## ✅ FAR AWAY Rules Compliance

### Team Eligibility
- [x] Team size: 1–5 members ✓
- [x] Cross-institution participation: allowed ✓

### Building Philosophy
- [x] Builder-first: actual working code, not slides only
- [x] AI tools used (LangChain, OpenAI) — declared ✓
- [x] Open-source libraries and frameworks used ✓
- [x] Original project (not a rebrand of existing work) ✓

### AI & Existing Projects
- [x] AI tools declared: LangChain, OpenAI GPT-4, YOLOv8, MediaPipe
- [x] Open-source frameworks declared: FastAPI, React, SQLAlchemy, Redis

### GitHub Requirements
- [x] Source code included ✓
- [x] Documentation included (README.md, docs/ARCHITECTURE.md) ✓
- [x] Setup instructions included (Quick Start in README) ✓
- [x] Relevant files included ✓

---

## 🚀 How to Run (for judges)

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/examguard-ai.git
cd examguard-ai

# 2. Set your API key (free option: Groq)
echo "GROQ_API_KEY=your-key-here" >> .env
echo "LLM_PROVIDER=groq" >> .env

# 3. Launch
docker-compose up --build

# 4. Open dashboard → http://localhost:3000
# 5. Run demo scenario
docker-compose --profile demo up demo_simulator
```

---

## 📽️ Demo Video Description

The demo shows:
1. Dashboard loads with a live exam session (score: 100/100, CLEAR)
2. `simulate_demo.py` fires — phone detected, second face appears, tab switches
3. Reasoning Agent LLM drops score to 34/100, verdict → COMPROMISED
4. Action Agent autonomously generates PDF incident report
5. Admin dashboard shows red alert toast + incident appears in log
6. PDF report downloadable from dashboard with AI reasoning trace

Total autonomous response time: **< 2 seconds** from anomaly to action.
