"""
Reports Router — handles PDF incident report upload (from Action Agent)
and retrieval (for dashboard download links).
"""

import os
import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from db.models import Incident

router = APIRouter()

REPORTS_DIR = os.getenv("REPORTS_DIR", "./reports")
Path(REPORTS_DIR).mkdir(parents=True, exist_ok=True)


@router.post("/upload", status_code=201)
async def upload_report(
    session_id: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Action Agent uploads a generated PDF report here.
    Stores the file and links it to the most recent incident for the session.
    """
    dest_path = os.path.join(REPORTS_DIR, file.filename)
    with open(dest_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Link to most recent incident for this session
    result = await db.execute(
        select(Incident)
        .where(Incident.session_id == session_id)
        .order_by(Incident.timestamp.desc())
        .limit(1)
    )
    incident = result.scalar_one_or_none()
    report_url = f"/api/v1/reports/{file.filename}"

    if incident:
        await db.execute(
            update(Incident).where(Incident.id == incident.id).values(report_url=report_url)
        )
        await db.commit()

    return {"filename": file.filename, "report_url": report_url}


@router.get("/{filename}")
async def download_report(filename: str):
    filepath = os.path.join(REPORTS_DIR, filename)
    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(filepath, media_type="application/pdf", filename=filename)
