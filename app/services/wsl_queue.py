from __future__ import annotations

import logging
from pathlib import Path

import orjson
from sqlalchemy.orm import Session

from app.services.system_posts import create_system_post

logger = logging.getLogger(__name__)


def _swap_queue_file(queue_path: Path) -> Path | None:
    if not queue_path.exists() or queue_path.stat().st_size == 0:
        return None
    processing_path = queue_path.with_suffix(".processing")
    queue_path.replace(processing_path)
    return processing_path


def drain_wsl_queue(db: Session, queue_path: Path) -> int:
    processing_path = _swap_queue_file(queue_path)
    if not processing_path:
        return 0

    created = 0
    try:
        with processing_path.open("rb") as fh:
            for raw_line in fh:
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    payload = orjson.loads(line)
                    create_system_post(
                        db,
                        status=str(payload.get("status", "OK")),
                        job_name=str(payload.get("job_name", "codex-run")),
                        human_text=str(payload.get("human_text", ""))[:280],
                        result_summary=str(payload.get("result_summary", "")),
                        error_summary=str(payload.get("error_summary", "")),
                        tags_csv=str(payload.get("tags_csv", "system,progress,codex")),
                        raw_payload=payload.get("raw_payload"),
                    )
                    created += 1
                except Exception:
                    logger.exception("Failed to import queued WSL progress line")
    finally:
        try:
            processing_path.unlink(missing_ok=True)
        except Exception:
            logger.exception("Failed to remove processing queue file")

    return created
