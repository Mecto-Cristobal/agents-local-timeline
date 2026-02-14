from __future__ import annotations

from typing import TypeVar

from sqlalchemy.orm import Session

ModelT = TypeVar("ModelT")


def save_and_refresh(db: Session, model: ModelT) -> ModelT:
    db.add(model)
    db.commit()
    db.refresh(model)
    return model
