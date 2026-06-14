"""
Pydantic schemas for request/response validation.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


# ── Session schemas ───────────────────────────────────────────────

class SessionCreate(BaseModel):
    id:         str
    student_id: str
    exam_id:    str


class SessionResponse(BaseModel):
    id:              str
    student_id:      str
    exam_id:         str
    started_at:      datetime
    ended_at:        Optional[datetime]
    integrity_score: int
    verdict:         str
    is_active:       bool

    class Config:
        from_attributes = True


# ── Incident schemas ──────────────────────────────────────────────

class IncidentCreate(BaseModel):
    session_id:      str
    timestamp:       str
    integrity_score: int
    verdict:         str
    reasoning:       str
    triggered_by:    List[str] = []


class IncidentResponse(BaseModel):
    id:              int
    session_id:      str
    timestamp:       datetime
    integrity_score: int
    verdict:         str
    reasoning:       str
    triggered_by:    List[str]
    report_url:      Optional[str]

    class Config:
        from_attributes = True


# ── Audit event schemas ───────────────────────────────────────────

class AuditEventCreate(BaseModel):
    session_id:  str
    event_type:  str
    severity:    str
    confidence:  float
    description: str
    metadata:    dict = {}


class AuditEventResponse(AuditEventCreate):
    id:        int
    timestamp: datetime

    class Config:
        from_attributes = True


# ── Stats schema ──────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_sessions:    int
    active_sessions:   int
    total_incidents:   int
    compromised_count: int
    suspicious_count:  int
    avg_integrity:     float
