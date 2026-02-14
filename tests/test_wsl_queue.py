from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.base import Base
from app.models.post import Post
from app.services.wsl_queue import drain_wsl_queue


def test_drain_wsl_queue():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    queue = Path("data") / f"wsl_post_queue_test_{uuid4().hex}.ndjson"
    queue.write_text(
        '{"status":"OK","job_name":"codex-run","human_text":"queued from wsl","tags_csv":"system,progress,codex"}\n',
        encoding="utf-8",
    )

    db = session_local()
    try:
        created = drain_wsl_queue(db, queue)
        assert created == 1
        posts = db.query(Post).all()
        assert len(posts) == 1
        assert posts[0].human_text == "queued from wsl"
    finally:
        db.close()
        queue.unlink(missing_ok=True)
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
