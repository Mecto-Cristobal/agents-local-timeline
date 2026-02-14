from __future__ import annotations

from datetime import datetime
from typing import Any

import orjson
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.post import Post
from app.schemas.post import PostCreate, PostOut, PostUpdate
from app.services.broadcast import EventPayload
from app.services.posts import (
    create_post,
    delete_post,
    get_post,
    list_posts,
    update_post,
)

router = APIRouter(prefix="/api/agents/posts", tags=["posts"])


def _normalize_raw_payload(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return orjson.dumps(value, option=orjson.OPT_INDENT_2).decode("utf-8")


@router.post("", response_model=PostOut)
async def create_post_api(
    payload: PostCreate,
    background: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    post = Post(**payload.model_dump())
    post.raw_payload_json = _normalize_raw_payload(payload.raw_payload_json)
    post = create_post(db, post)

    async def _publish() -> None:
        event = EventPayload(
            event="new_post",
            data={
                "post_id": post.id,
                "created_at": post.created_at.isoformat(),
                "account_id": post.account_id,
            },
            created_at=datetime.utcnow(),
        )
        await request.app.state.broadcaster.publish(event)

    background.add_task(_publish)
    return post


@router.patch("/{post_id}", response_model=PostOut)
async def update_post_api(
    post_id: int,
    payload: PostUpdate,
    db: Session = Depends(get_db),
):
    post = get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    update_data = payload.model_dump(exclude_unset=True)
    if "raw_payload_json" in update_data:
        update_data["raw_payload_json"] = _normalize_raw_payload(
            update_data["raw_payload_json"]
        )
    for key, value in update_data.items():
        setattr(post, key, value)
    return update_post(db, post)


@router.get("", response_model=list[PostOut])
async def list_posts_api(
    account_id: int | None = None,
    status: str | None = None,
    tag: str | None = None,
    since: datetime | None = None,
    limit: int = 50,
    q: str | None = None,
    db: Session = Depends(get_db),
):
    return list_posts(
        db,
        account_id=account_id,
        status=status,
        tag=tag,
        since=since,
        limit=limit,
        q=q,
    )


@router.delete("/{post_id}")
async def delete_post_api(
    post_id: int,
    db: Session = Depends(get_db),
):
    post = get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    delete_post(db, post)
    return {"status": "deleted", "post_id": post_id}
