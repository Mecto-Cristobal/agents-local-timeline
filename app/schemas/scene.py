from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SceneBase(BaseModel):
    account_id: int | None = None
    name: str = Field(max_length=200)
    scene_json: str = Field(default="")


class SceneCreate(SceneBase):
    pass


class SceneUpdate(BaseModel):
    account_id: int | None = None
    name: str | None = Field(default=None, max_length=200)
    scene_json: str | None = None


class SceneOut(SceneBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
