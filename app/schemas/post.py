from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class PostBase(BaseModel):
    account_id: int | None = None
    status: str = Field(default="OK")
    job_name: str = Field(default="")
    env: str = Field(default="")
    version: str = Field(default="")
    when_ts: datetime | None = None

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

    tags_csv: str = Field(default="")
    raw_payload_json: str = Field(default="")


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    account_id: int | None = None
    status: str | None = None
    job_name: str | None = None
    env: str | None = None
    version: str | None = None
    when_ts: datetime | None = None
    goal: str | None = None
    result_summary: str | None = None
    latency_p95_ms: float | None = None
    tokens: int | None = None
    cost_usd: float | None = None
    retries: int | None = None
    anomaly_summary: str | None = None
    error_summary: str | None = None
    data_deps_summary: str | None = None
    next_action: str | None = None
    tags_csv: str | None = None
    raw_payload_json: str | None = None


class PostOut(PostBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
