from __future__ import annotations

import logging
import os

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import APP_DESCRIPTION, APP_TITLE
from app.db.session import SessionLocal
from app.routers import api_accounts, api_posts, api_scenes, api_system, events, pages
from app.services.broadcast import Broadcaster
from app.services.system_posts import create_system_post

logging.basicConfig(level=logging.INFO)

app = FastAPI(title=APP_TITLE, description=APP_DESCRIPTION)

app.state.broadcaster = Broadcaster()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(pages.router)
app.include_router(api_posts.router)
app.include_router(api_scenes.router)
app.include_router(api_accounts.router)
app.include_router(api_system.router)
app.include_router(events.router)


@app.on_event("startup")
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
    except Exception:
        logging.exception("Bootstrap post failed")
    finally:
        db.close()


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
