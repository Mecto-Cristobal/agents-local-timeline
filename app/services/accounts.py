from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.account import Account


def get_account(db: Session, account_id: int) -> Account | None:
    return db.get(Account, account_id)


def list_accounts(db: Session) -> list[Account]:
    stmt = select(Account).order_by(Account.name)
    return list(db.execute(stmt).scalars().all())


def upsert_account(db: Session, account: Account) -> Account:
    db.add(account)
    db.commit()
    db.refresh(account)
    return account
