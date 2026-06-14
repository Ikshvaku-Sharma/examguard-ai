"""
Stats Router — aggregate metrics for the dashboard home screen.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from db.models import Incident, Session as SessionModel
from models.schemas import DashboardStats

router = APIRouter()


@router.get("/", response_model=DashboardStats)
async def get_stats(db: AsyncSession = Depends(get_db)):
    total_sessions  = (await db.execute(select(func.count(SessionModel.id)))).scalar() or 0
    active_sessions = (await db.execute(
        select(func.count(SessionModel.id)).where(SessionModel.is_active == True)
    )).scalar() or 0
    total_incidents = (await db.execute(select(func.count(Incident.id)))).scalar() or 0

    compromised = (await db.execute(
        select(func.count(SessionModel.id)).where(SessionModel.verdict == "COMPROMISED")
    )).scalar() or 0
    suspicious = (await db.execute(
        select(func.count(SessionModel.id)).where(SessionModel.verdict == "SUSPICIOUS")
    )).scalar() or 0

    avg_score = (await db.execute(select(func.avg(SessionModel.integrity_score)))).scalar()
    avg_integrity = round(float(avg_score), 1) if avg_score is not None else 100.0

    return DashboardStats(
        total_sessions    = total_sessions,
        active_sessions   = active_sessions,
        total_incidents   = total_incidents,
        compromised_count = compromised,
        suspicious_count  = suspicious,
        avg_integrity     = avg_integrity,
    )
