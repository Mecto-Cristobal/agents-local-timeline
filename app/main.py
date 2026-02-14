from __future__ import annotations

import asyncio
import contextlib
import logging
import os
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import APP_DESCRIPTION, APP_TITLE, WSL_QUEUE_PATH
from app.db.session import SessionLocal
from app.routers import api_accounts, api_posts, api_scenes, api_system, events, pages
from app.services.broadcast import Broadcaster
from app.services.system_posts import create_system_post, post_update_if_changed
from app.services.wsl_queue import drain_wsl_queue

logging.basicConfig(level=logging.INFO)

def bootstrap_system_post() -> None:
    if os.getenv("PYTEST_CURRENT_TEST"):
        return
    if os.getenv("AGENTS_SKIP_BOOTSTRAP"):
        return
    db = SessionLocal()
    try:
        create_system_post(
            db,
            status="OK",
            job_name="agents-timeline",
            human_text="AGENTS started. Ready to receive agent progress posts.",
            result_summary="Startup completed",
            tags_csv="system,boot",
        )
        post_update_if_changed(db)
    except Exception:
        logging.exception("Bootstrap post failed")
    finally:
        db.close()


async def _wsl_queue_worker() -> None:
    while True:
        db = SessionLocal()
        try:
            imported = drain_wsl_queue(db, WSL_QUEUE_PATH)
            if imported:
                logging.info("Imported %s queued WSL progress posts", imported)
        except Exception:
            logging.exception("WSL queue worker failed")
        finally:
            db.close()
        await asyncio.sleep(2)


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    bootstrap_system_post()
    task = asyncio.create_task(_wsl_queue_worker())
    app.state.wsl_queue_task = task
    try:
        yield
    finally:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task


app = FastAPI(title=APP_TITLE, description=APP_DESCRIPTION, lifespan=lifespan)

app.state.broadcaster = Broadcaster()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(pages.router)
app.include_router(api_posts.router)
app.include_router(api_scenes.router)
app.include_router(api_accounts.router)
app.include_router(api_system.router)
app.include_router(events.router)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    db = SessionLocal()
    try:
        create_system_post(
            db,
            status="FAIL",
            job_name="agents-timeline",
            human_text="Unhandled exception captured by server guard.",
            result_summary="Request failed",
            error_summary=str(exc)[:1000],
            tags_csv="system,incident",
            raw_payload={"path": str(request.url.path), "method": request.method},
        )
    except Exception:
        logging.exception("Failed to write incident post")
    finally:
        db.close()
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


@app.get("/")
async def root():
    return {"message": "Visit /AGENTS"}


@app.get("/agents")
async def lower_agents():
    return RedirectResponse(url="/AGENTS")
