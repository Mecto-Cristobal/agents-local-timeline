from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import POST_HUMAN_TEXT_MAX_CHARS
from app.db.session import get_db
from app.schemas.post import PostOut
from app.services.system_posts import create_system_post

router = APIRouter(prefix="/api/agents/system", tags=["System"])


class SystemProgressIn(BaseModel):
    status: str = Field(default="OK")
    job_name: str = Field(default="agent-progress", max_length=200)
    env: str = Field(default="", max_length=100)
    version: str = Field(default="", max_length=100)
    when_ts: datetime | None = None
    human_text: str = Field(max_length=POST_HUMAN_TEXT_MAX_CHARS)
    goal: str = Field(default="")
    result_summary: str = Field(default="")
    latency_p95_ms: float | None = None
    tokens: int | None = None
    cost_usd: float | None = None
    retries: int | None = None
    anomaly_summary: str = Field(default="")
    error_summary: str = Field(default="")
    data_deps_summary: str = Field(default="")
    next_action: str = Field(default="")
    tags_csv: str = Field(default="system,progress")
    raw_payload: dict | None = None


@router.post("/progress", response_model=PostOut)
async def post_progress(payload: SystemProgressIn, db: Session = Depends(get_db)):
    return create_system_post(
        db,
        status=payload.status,
        job_name=payload.job_name,
        env=payload.env,
        version=payload.version,
        when_ts=payload.when_ts,
        human_text=payload.human_text,
        goal=payload.goal,
        result_summary=payload.result_summary,
        latency_p95_ms=payload.latency_p95_ms,
        tokens=payload.tokens,
        cost_usd=payload.cost_usd,
        retries=payload.retries,
        anomaly_summary=payload.anomaly_summary,
        error_summary=payload.error_summary,
        data_deps_summary=payload.data_deps_summary,
        next_action=payload.next_action,
        tags_csv=payload.tags_csv,
        raw_payload=payload.raw_payload,
    )
