from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.scene import Scene


def create_scene(db: Session, scene: Scene) -> Scene:
    db.add(scene)
    db.commit()
    db.refresh(scene)
    return scene


def update_scene(db: Session, scene: Scene) -> Scene:
    db.add(scene)
    db.commit()
    db.refresh(scene)
    return scene


def get_scene(db: Session, scene_id: int) -> Scene | None:
    return db.get(Scene, scene_id)


def list_scenes(db: Session, account_id: int | None = None) -> list[Scene]:
    stmt = select(Scene)
    if account_id is not None:
        stmt = stmt.where(Scene.account_id == account_id)
    stmt = stmt.order_by(Scene.updated_at.desc())
    return list(db.execute(stmt).scalars().all())
