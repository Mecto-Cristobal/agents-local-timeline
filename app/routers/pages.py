from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.account import Account
from app.models.post import Post, PostStatus
from app.services.accounts import list_accounts, upsert_account
from app.services.posts import create_post, list_posts

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/AGENTS", response_class=HTMLResponse)
async def agents_home(request: Request, db: Session = Depends(get_db)):
    accounts = list_accounts(db)
    posts = list_posts(db, limit=50)
    last_seen = datetime.now(tz=timezone.utc).isoformat()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "accounts": accounts,
            "posts": posts,
            "last_seen": last_seen,
        },
    )


@router.get("/partials/timeline", response_class=HTMLResponse)
async def timeline_partial(request: Request, db: Session = Depends(get_db)):
    posts = list_posts(db, limit=50)
    last_seen = datetime.now(tz=timezone.utc).isoformat()
    return templates.TemplateResponse(
        "partials/timeline.html",
        {"request": request, "posts": posts, "last_seen": last_seen},
    )


@router.post("/accounts/create", response_class=HTMLResponse)
async def create_account_form(
    request: Request,
    name: str = Form(...),
    color: str = Form("#4b5563"),
    db: Session = Depends(get_db),
):
    account = Account(name=name, color=color)
    upsert_account(db, account)
    accounts = list_accounts(db)
    return templates.TemplateResponse(
        "partials/accounts_list.html", {"request": request, "accounts": accounts}
    )


@router.post("/accounts/{account_id}", response_class=HTMLResponse)
async def update_account_form(
    request: Request,
    account_id: int,
    name: str = Form(...),
    color: str = Form("#4b5563"),
    db: Session = Depends(get_db),
):
    account = db.get(Account, account_id)
    if account:
        account.name = name
        account.color = color
        upsert_account(db, account)
    accounts = list_accounts(db)
    return templates.TemplateResponse(
        "partials/accounts_list.html", {"request": request, "accounts": accounts}
    )


@router.post("/posts/create", response_class=HTMLResponse)
async def create_post_form(
    request: Request,
    account_id: str | None = Form(None),
    status: str = Form("OK"),
    job_name: str = Form(""),
    goal: str = Form(""),
    result_summary: str = Form(""),
    tags_csv: str = Form(""),
    db: Session = Depends(get_db),
):
    parsed_account_id = int(account_id) if account_id else None
    valid_status = status if status in PostStatus.__members__ else "OK"
    post = Post(
        account_id=parsed_account_id,
        status=valid_status,
        job_name=job_name,
        goal=goal,
        result_summary=result_summary,
        tags_csv=tags_csv,
    )
    create_post(db, post)
    posts = list_posts(db, limit=50)
    last_seen = datetime.now(tz=timezone.utc).isoformat()
    return templates.TemplateResponse(
        "partials/timeline.html",
        {"request": request, "posts": posts, "last_seen": last_seen},
    )
