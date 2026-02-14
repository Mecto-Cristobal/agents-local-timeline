from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path

import orjson
from sqlalchemy.orm import Session

from app.core.config import POST_HUMAN_TEXT_MAX_CHARS
from app.models.account import Account
from app.models.post import Post
from app.services.persistence import save_and_refresh

SYSTEM_ACCOUNT_NAME = "AGENTS System"
SYSTEM_ACCOUNT_COLOR = "#2f6fb2"
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def build_code_signature() -> str:
    """Build a compact signature from tracked source file mtimes/sizes."""
    roots = [PROJECT_ROOT / "app", PROJECT_ROOT / "migrations", PROJECT_ROOT / "AGENTS.md"]
    hasher = hashlib.sha256()
    for root in roots:
        if root.is_file():
            stat = root.stat()
            hasher.update(f"{root}:{stat.st_mtime_ns}:{stat.st_size}".encode("utf-8"))
            continue
        if not root.exists():
            continue
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            stat = path.stat()
            rel = path.relative_to(PROJECT_ROOT)
            hasher.update(f"{rel}:{stat.st_mtime_ns}:{stat.st_size}".encode("utf-8"))
    return hasher.hexdigest()[:16]


def ensure_system_account(db: Session) -> Account:
    account = db.query(Account).filter(Account.name == SYSTEM_ACCOUNT_NAME).first()
    if account:
        return account
    account = Account(name=SYSTEM_ACCOUNT_NAME, color=SYSTEM_ACCOUNT_COLOR, settings_json={})
    return save_and_refresh(db, account)


def create_system_post(
    db: Session,
    *,
    status: str,
    job_name: str,
    env: str = "",
    version: str = "",
    when_ts: datetime | None = None,
    human_text: str,
    goal: str = "",
    result_summary: str = "",
    latency_p95_ms: float | None = None,
    tokens: int | None = None,
    cost_usd: float | None = None,
    retries: int | None = None,
    anomaly_summary: str = "",
    error_summary: str = "",
    data_deps_summary: str = "",
    next_action: str = "",
    tags_csv: str = "system,progress",
    raw_payload: dict | None = None,
) -> Post:
    account = ensure_system_account(db)
    post = Post(
        account_id=account.id,
        status=status,
        job_name=job_name,
        env=env,
        version=version,
        when_ts=when_ts,
        human_text=human_text[:POST_HUMAN_TEXT_MAX_CHARS],
        goal=goal,
        result_summary=result_summary,
        latency_p95_ms=latency_p95_ms,
        tokens=tokens,
        cost_usd=cost_usd,
        retries=retries,
        anomaly_summary=anomaly_summary,
        error_summary=error_summary,
        data_deps_summary=data_deps_summary,
        next_action=next_action,
        tags_csv=tags_csv,
        raw_payload_json=(
            orjson.dumps(raw_payload, option=orjson.OPT_INDENT_2).decode("utf-8")
            if raw_payload
            else ""
        ),
    )
    return save_and_refresh(db, post)


def post_update_if_changed(db: Session) -> bool:
    """
    Post a progress report once per code signature.
    Returns True when a new report was created.
    """
    account = ensure_system_account(db)
    signature = build_code_signature()
    settings = dict(account.settings_json or {})
    last_signature = settings.get("last_reported_signature")
    if last_signature == signature:
        return False
    create_system_post(
        db,
        status="OK",
        job_name="agents-update",
        human_text="Code update detected and reported automatically.",
        result_summary=f"signature={signature}",
        tags_csv="system,progress,auto-report",
        raw_payload={"signature": signature, "previous_signature": last_signature},
    )
    settings["last_reported_signature"] = signature
    account.settings_json = settings
    save_and_refresh(db, account)
    return True
