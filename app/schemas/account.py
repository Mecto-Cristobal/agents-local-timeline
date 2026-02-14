from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class AccountBase(BaseModel):
    name: str = Field(max_length=200)
    color: str = Field(default="#4b5563", max_length=20)
    settings_json: dict = Field(default_factory=dict)


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    color: str | None = Field(default=None, max_length=20)
    settings_json: dict | None = None


class AccountOut(AccountBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
