"""
Integration tests for the Incidents API endpoints.
Run with: pytest tests/test_incidents_api.py

Requires the backend test DB to be configured (uses SQLite in-memory for tests).
"""

import os
import sys
import pytest
from httpx import AsyncClient, ASGITransport

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

# Use SQLite in-memory DB for tests
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from main import app  # noqa: E402


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_check(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_create_and_list_session(client):
    payload = {"id": "test_session_1", "student_id": "stu_1", "exam_id": "exam_1"}
    resp = await client.post("/api/v1/sessions/", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] == "test_session_1"
    assert data["integrity_score"] == 100
    assert data["verdict"] == "CLEAR"

    resp2 = await client.get("/api/v1/sessions/")
    assert resp2.status_code == 200
    assert any(s["id"] == "test_session_1" for s in resp2.json())


@pytest.mark.asyncio
async def test_create_incident_updates_session(client):
    # Create session first
    await client.post("/api/v1/sessions/", json={
        "id": "test_session_2", "student_id": "stu_2", "exam_id": "exam_1"
    })

    incident_payload = {
        "session_id": "test_session_2",
        "timestamp": "2026-06-12T10:00:00",
        "integrity_score": 35,
        "verdict": "COMPROMISED",
        "reasoning": "Phone detected and multiple faces seen.",
        "triggered_by": ["phone_detected", "multiple_faces"],
    }
    resp = await client.post("/api/v1/incidents/", json=incident_payload)
    assert resp.status_code == 201
    assert resp.json()["verdict"] == "COMPROMISED"

    # Session should now reflect updated score
    session_resp = await client.get("/api/v1/sessions/test_session_2")
    assert session_resp.json()["integrity_score"] == 35
    assert session_resp.json()["verdict"] == "COMPROMISED"


@pytest.mark.asyncio
async def test_stats_endpoint(client):
    resp = await client.get("/api/v1/stats/")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_sessions" in data
    assert "avg_integrity" in data
