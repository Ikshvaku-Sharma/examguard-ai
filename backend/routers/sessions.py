"""
Sessions Router — CRUD for exam sessions.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from db.models import Session as SessionModel
from models.schemas import SessionCreate, SessionResponse

router = APIRouter()


@router.post("/", response_model=SessionResponse, status_code=201)
async def create_session(body: SessionCreate, db: AsyncSession = Depends(get_db)):
    session = SessionModel(
        id         = body.id,
        student_id = body.student_id,
        exam_id    = body.exam_id,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


@router.get("/", response_model=list[SessionResponse])
async def list_sessions(active_only: bool = False, db: AsyncSession = Depends(get_db)):
    q = select(SessionModel)
    if active_only:
        q = q.where(SessionModel.is_active == True)
    result = await db.execute(q.order_by(SessionModel.started_at.desc()))
    return result.scalars().all()


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SessionModel).where(SessionModel.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.patch("/{session_id}/end", response_model=SessionResponse)
async def end_session(session_id: str, db: AsyncSession = Depends(get_db)):
    from datetime import datetime
    await db.execute(
        update(SessionModel)
        .where(SessionModel.id == session_id)
        .values(is_active=False, ended_at=datetime.utcnow())
    )
    await db.commit()
    result = await db.execute(select(SessionModel).where(SessionModel.id == session_id))
    return result.scalar_one_or_none()
