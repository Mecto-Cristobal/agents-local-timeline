from __future__ import annotations

import orjson
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.post import Post

SYSTEM_ACCOUNT_NAME = "AGENTS System"
SYSTEM_ACCOUNT_COLOR = "#2f6fb2"


def ensure_system_account(db: Session) -> Account:
    account = db.query(Account).filter(Account.name == SYSTEM_ACCOUNT_NAME).first()
    if account:
        return account
    account = Account(name=SYSTEM_ACCOUNT_NAME, color=SYSTEM_ACCOUNT_COLOR, settings_json={})
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def create_system_post(
    db: Session,
    *,
    status: str,
    job_name: str,
    human_text: str,
    result_summary: str = "",
    error_summary: str = "",
    tags_csv: str = "system,progress",
    raw_payload: dict | None = None,
) -> Post:
    account = ensure_system_account(db)
    post = Post(
        account_id=account.id,
        status=status,
        job_name=job_name,
        human_text=human_text[:280],
        result_summary=result_summary,
        error_summary=error_summary,
        tags_csv=tags_csv,
        raw_payload_json=(
            orjson.dumps(raw_payload, option=orjson.OPT_INDENT_2).decode("utf-8")
            if raw_payload
            else ""
        ),
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post
