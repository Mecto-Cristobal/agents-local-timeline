from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.account import Account
from app.schemas.account import AccountCreate, AccountOut, AccountUpdate
from app.services.accounts import get_account, list_accounts, upsert_account

router = APIRouter(prefix="/api/agents/accounts", tags=["accounts"])


@router.get("", response_model=list[AccountOut])
async def list_accounts_api(db: Session = Depends(get_db)):
    return list_accounts(db)


@router.post("", response_model=AccountOut)
async def create_account_api(payload: AccountCreate, db: Session = Depends(get_db)):
    account = Account(**payload.model_dump())
    return upsert_account(db, account)


@router.patch("/{account_id}", response_model=AccountOut)
async def update_account_api(
    account_id: int, payload: AccountUpdate, db: Session = Depends(get_db)
):
    account = get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(account, key, value)
    return upsert_account(db, account)
