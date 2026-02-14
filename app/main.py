from __future__ import annotations

import logging
import os

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.core.config import APP_DESCRIPTION, APP_TITLE
from app.db.session import SessionLocal
from app.models.account import Account
from app.models.post import Post
from app.routers import api_accounts, api_posts, api_scenes, events, pages
from app.services.broadcast import Broadcaster

logging.basicConfig(level=logging.INFO)

app = FastAPI(title=APP_TITLE, description=APP_DESCRIPTION)

app.state.broadcaster = Broadcaster()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(pages.router)
app.include_router(api_posts.router)
app.include_router(api_scenes.router)
app.include_router(api_accounts.router)
app.include_router(events.router)


@app.on_event("startup")
def bootstrap_system_post() -> None:
    if os.getenv("PYTEST_CURRENT_TEST"):
        return
    if os.getenv("AGENTS_SKIP_BOOTSTRAP"):
        return
    db = SessionLocal()
    try:
        has_posts = db.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='posts'")
        ).first()
        if not has_posts:
            return
        existing = db.query(Post).count()
        if existing > 0:
            return
        account = db.query(Account).filter(Account.name == "AGENTS System").first()
        if not account:
            account = Account(name="AGENTS System", color="#2f6fb2", settings_json={})
            db.add(account)
            db.commit()
            db.refresh(account)
        post = Post(
            account_id=account.id,
            status="OK",
            job_name="agents-timeline",
            goal="Boot local agents SNS",
            result_summary="System initialized",
            tags_csv="system,boot",
        )
        db.add(post)
        db.commit()
    except Exception:
        logging.exception("Bootstrap post failed")
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": "Visit /AGENTS"}


@app.get("/agents")
async def lower_agents():
    return RedirectResponse(url="/AGENTS")
