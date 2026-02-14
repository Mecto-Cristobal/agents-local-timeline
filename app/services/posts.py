from __future__ import annotations

from datetime import datetime

from sqlalchemy import Select, and_, desc, select, text
from sqlalchemy.orm import Session

from app.models.post import Post


def create_post(db: Session, post: Post) -> Post:
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def update_post(db: Session, post: Post) -> Post:
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def get_post(db: Session, post_id: int) -> Post | None:
    return db.get(Post, post_id)


def list_posts(
    db: Session,
    account_id: int | None = None,
    status: str | None = None,
    tag: str | None = None,
    since: datetime | None = None,
    limit: int = 50,
    q: str | None = None,
) -> list[Post]:
    if q:
        sql = text(
            """
            SELECT p.id FROM posts p
            JOIN posts_fts fts ON p.id = fts.rowid
            WHERE fts MATCH :q
            ORDER BY p.created_at DESC
            LIMIT :limit
            """
        )
        ids = [row[0] for row in db.execute(sql, {"q": q, "limit": limit}).all()]
        if not ids:
            return []
        stmt = select(Post).where(Post.id.in_(ids)).order_by(desc(Post.created_at))
        return list(db.execute(stmt).scalars().all())

    stmt: Select = select(Post)
    filters = []
    if account_id is not None:
        filters.append(Post.account_id == account_id)
    if status:
        filters.append(Post.status == status)
    if tag:
        filters.append(Post.tags_csv.like(f"%{tag}%"))
    if since:
        filters.append(Post.created_at > since)
    if filters:
        stmt = stmt.where(and_(*filters))
    stmt = stmt.order_by(desc(Post.created_at)).limit(limit)
    return list(db.execute(stmt).scalars().all())
