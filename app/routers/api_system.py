from __future__ import annotations

from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.post import PostOut
from app.services.system_posts import create_system_post

router = APIRouter(prefix="/api/agents/system", tags=["System"])


class SystemProgressIn(BaseModel):
    status: str = Field(default="OK")
    job_name: str = Field(default="agent-progress", max_length=200)
    human_text: str = Field(max_length=280)
    result_summary: str = Field(default="")
    error_summary: str = Field(default="")
    tags_csv: str = Field(default="system,progress")
    raw_payload: dict | None = None


@router.post("/progress", response_model=PostOut)
async def post_progress(payload: SystemProgressIn, db: Session = Depends(get_db)):
    return create_system_post(
        db,
        status=payload.status,
        job_name=payload.job_name,
        human_text=payload.human_text,
        result_summary=payload.result_summary,
        error_summary=payload.error_summary,
        tags_csv=payload.tags_csv,
        raw_payload=payload.raw_payload,
    )
