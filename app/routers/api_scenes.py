from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.scene import Scene
from app.schemas.scene import SceneCreate, SceneOut, SceneUpdate
from app.services.scenes import create_scene, get_scene, list_scenes, update_scene

router = APIRouter(prefix="/api/agents/scenes", tags=["scenes"])


@router.post("", response_model=SceneOut)
async def create_scene_api(payload: SceneCreate, db: Session = Depends(get_db)):
    scene = Scene(**payload.model_dump())
    return create_scene(db, scene)


@router.get("", response_model=list[SceneOut])
async def list_scenes_api(account_id: int | None = None, db: Session = Depends(get_db)):
    return list_scenes(db, account_id=account_id)


@router.put("/{scene_id}", response_model=SceneOut)
async def update_scene_api(
    scene_id: int, payload: SceneUpdate, db: Session = Depends(get_db)
):
    scene = get_scene(db, scene_id)
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(scene, key, value)
    return update_scene(db, scene)
