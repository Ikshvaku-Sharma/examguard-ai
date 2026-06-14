"""
SQLAlchemy ORM models for ExamGuard AI.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, DateTime, Float, ForeignKey,
    Integer, String, Text, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base


class Session(Base):
    __tablename__ = "sessions"

    id:             Mapped[str]      = mapped_column(String(64),  primary_key=True)
    student_id:     Mapped[str]      = mapped_column(String(64),  nullable=False)
    exam_id:        Mapped[str]      = mapped_column(String(64),  nullable=False)
    started_at:     Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ended_at:       Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    integrity_score: Mapped[int]     = mapped_column(Integer, default=100)
    verdict:        Mapped[str]      = mapped_column(String(20),  default="CLEAR")
    is_active:      Mapped[bool]     = mapped_column(Boolean, default=True)

    incidents:  Mapped[list["Incident"]]   = relationship(back_populates="session", cascade="all, delete")
    audit_events: Mapped[list["AuditEvent"]] = relationship(back_populates="session", cascade="all, delete")


class Incident(Base):
    __tablename__ = "incidents"

    id:              Mapped[int]     = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id:      Mapped[str]     = mapped_column(ForeignKey("sessions.id"), nullable=False)
    timestamp:       Mapped[datetime]= mapped_column(DateTime, default=datetime.utcnow)
    integrity_score: Mapped[int]     = mapped_column(Integer)
    verdict:         Mapped[str]     = mapped_column(String(20))
    reasoning:       Mapped[str]     = mapped_column(Text)
    triggered_by:    Mapped[list]    = mapped_column(JSON, default=list)
    report_url:      Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    session: Mapped["Session"] = relationship(back_populates="incidents")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id:          Mapped[int]      = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id:  Mapped[str]      = mapped_column(ForeignKey("sessions.id"), nullable=False)
    timestamp:   Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    event_type:  Mapped[str]      = mapped_column(String(50))
    severity:    Mapped[str]      = mapped_column(String(10))
    confidence:  Mapped[float]    = mapped_column(Float)
    description: Mapped[str]      = mapped_column(Text)
    metadata:    Mapped[dict]     = mapped_column(JSON, default=dict)
    frame_b64:   Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    session: Mapped["Session"] = relationship(back_populates="audit_events")
