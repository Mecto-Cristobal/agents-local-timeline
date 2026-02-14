from __future__ import annotations

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.post import Post
from app.models.scene import Scene


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


def delete_account(db: Session, account: Account, cascade: bool = False) -> None:
    if cascade:
        db.execute(delete(Post).where(Post.account_id == account.id))
        db.execute(delete(Scene).where(Scene.account_id == account.id))
    else:
        db.execute(update(Post).where(Post.account_id == account.id).values(account_id=None))
        db.execute(update(Scene).where(Scene.account_id == account.id).values(account_id=None))
    db.delete(account)
    db.commit()
