"""
ExamGuard AI — FastAPI Backend
────────────────────────────────
Central API server. Handles:
  - REST endpoints for sessions, incidents, reports
  - WebSocket for real-time dashboard updates
  - Redis subscriber that forwards events to connected WS clients
"""

import asyncio
import json
import logging
import os
from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from db.database import init_db
from routers import sessions, incidents, reports, stats

logging.basicConfig(level=logging.INFO, format="%(asctime)s [BACKEND] %(message)s")
log = logging.getLogger(__name__)

REDIS_URL    = os.getenv("REDIS_URL",    "redis://localhost:6379")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")


# ── WebSocket connection manager ──────────────────────────────────

class ConnectionManager:
    def __init__(self):
        self._connections: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self._connections.append(ws)
        log.info("WS client connected. Total: %d", len(self._connections))

    def disconnect(self, ws: WebSocket):
        self._connections.remove(ws)
        log.info("WS client disconnected. Total: %d", len(self._connections))

    async def broadcast(self, data: dict):
        dead = []
        for ws in self._connections:
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self._connections.remove(ws)


manager = ConnectionManager()


# ── Redis → WebSocket bridge ──────────────────────────────────────

async def redis_listener(app: FastAPI):
    """
    Subscribes to Redis channels and forwards messages
    to all connected WebSocket clients.
    """
    redis = await aioredis.from_url(REDIS_URL, decode_responses=True)
    pubsub = redis.pubsub()
    await pubsub.subscribe("anomalies", "alerts", "reasoning_results")
    log.info("Backend subscribed to Redis channels")

    async for message in pubsub.listen():
        if message["type"] != "message":
            continue
        try:
            payload = {
                "channel": message["channel"],
                "data":    json.loads(message["data"]),
            }
            await manager.broadcast(payload)
        except Exception as exc:
            log.error("Redis→WS bridge error: %s", exc)


# ── App lifecycle ─────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    task = asyncio.create_task(redis_listener(app))
    log.info("ExamGuard Backend ready 🚀")
    yield
    task.cancel()


# ── App ───────────────────────────────────────────────────────────

app = FastAPI(
    title="ExamGuard AI",
    description="Autonomous Exam Integrity Monitor — FAR AWAY 2026",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(sessions.router,  prefix="/api/v1/sessions",  tags=["Sessions"])
app.include_router(incidents.router, prefix="/api/v1/incidents", tags=["Incidents"])
app.include_router(reports.router,   prefix="/api/v1/reports",   tags=["Reports"])
app.include_router(stats.router,     prefix="/api/v1/stats",     tags=["Stats"])


# ── WebSocket endpoint ────────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep alive — client can also send pings
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ── Health check ──────────────────────────────────────────────────

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "service": "examguard-backend"}
