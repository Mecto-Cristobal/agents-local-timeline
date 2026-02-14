from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import APP_DESCRIPTION, APP_TITLE
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


@app.get("/")
async def root():
    return {"message": "Visit /AGENTS"}


@app.get("/agents")
async def lower_agents():
    return RedirectResponse(url="/AGENTS")
