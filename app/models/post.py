from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class PostStatus(str, Enum):
    OK = "OK"
    WARN = "WARN"
    FAIL = "FAIL"


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"), index=True)
    status: Mapped[str] = mapped_column(String(10), default=PostStatus.OK.value)
    job_name: Mapped[str] = mapped_column(String(200), default="")
    env: Mapped[str] = mapped_column(String(100), default="")
    version: Mapped[str] = mapped_column(String(100), default="")
    when_ts: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    goal: Mapped[str] = mapped_column(Text, default="")
    result_summary: Mapped[str] = mapped_column(Text, default="")

    latency_p95_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cost_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    retries: Mapped[int | None] = mapped_column(Integer, nullable=True)

    anomaly_summary: Mapped[str] = mapped_column(Text, default="")
    error_summary: Mapped[str] = mapped_column(Text, default="")
    data_deps_summary: Mapped[str] = mapped_column(Text, default="")
    next_action: Mapped[str] = mapped_column(Text, default="")

    tags_csv: Mapped[str] = mapped_column(String(400), default="")
    raw_payload_json: Mapped[str] = mapped_column(Text, default="")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )

    account = relationship("Account")
