"""
Incidents Router — stores and retrieves integrity incidents.
Called by the Action Agent when a session is flagged.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from db.database import get_db
from db.models import Incident, Session as SessionModel
from models.schemas import IncidentCreate, IncidentResponse

router = APIRouter()


@router.post("/", response_model=IncidentResponse, status_code=201)
async def create_incident(body: IncidentCreate, db: AsyncSession = Depends(get_db)):
    # Upsert session score + verdict
    await db.execute(
        update(SessionModel)
        .where(SessionModel.id == body.session_id)
        .values(integrity_score=body.integrity_score, verdict=body.verdict)
    )

    incident = Incident(
        session_id      = body.session_id,
        timestamp       = datetime.fromisoformat(body.timestamp),
        integrity_score = body.integrity_score,
        verdict         = body.verdict,
        reasoning       = body.reasoning,
        triggered_by    = body.triggered_by,
    )
    db.add(incident)
    await db.commit()
    await db.refresh(incident)
    return incident


@router.get("/", response_model=list[IncidentResponse])
async def list_incidents(
    session_id: str | None = None,
    verdict:    str | None = None,
    limit:      int        = 50,
    db: AsyncSession = Depends(get_db),
):
    q = select(Incident)
    if session_id:
        q = q.where(Incident.session_id == session_id)
    if verdict:
        q = q.where(Incident.verdict == verdict)
    q = q.order_by(Incident.timestamp.desc()).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(incident_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident
