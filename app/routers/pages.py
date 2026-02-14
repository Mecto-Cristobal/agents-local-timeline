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
from app.services.posts import create_post, delete_post, get_post, list_posts

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


def _paginate_posts(
    db: Session, page: int, limit: int, account_id: int | None = None
) -> tuple[list[Post], bool, int, int]:
    safe_page = max(page, 1)
    safe_limit = max(min(limit, 200), 1)
    offset = (safe_page - 1) * safe_limit
    posts = list_posts(
        db, limit=safe_limit + 1, offset=offset, account_id=account_id
    )
    has_next = len(posts) > safe_limit
    return posts[:safe_limit], has_next, safe_page, safe_limit


@router.get("/AGENTS", response_class=HTMLResponse)
async def agents_home(
    request: Request,
    page: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    accounts = list_accounts(db)
    posts, has_next, safe_page, safe_limit = _paginate_posts(db, page, limit)
    last_seen = datetime.now(tz=timezone.utc).isoformat()
    context = {
        "request": request,
        "accounts": accounts,
        "posts": posts,
        "last_seen": last_seen,
        "page": safe_page,
        "limit": safe_limit,
        "has_next": has_next,
        "title": "Timeline",
        "subtitle": "Latest first",
        "content_template": "partials/page_timeline.html",
    }
    if request.headers.get("HX-Request") == "true":
        return templates.TemplateResponse("partials/page_timeline.html", context)
    return templates.TemplateResponse("index.html", context)


@router.get("/AGENTS/accounts", response_class=HTMLResponse)
@router.get("/AGENTS/post", response_class=HTMLResponse)
@router.get("/AGENTS/3d", response_class=HTMLResponse)
@router.get("/AGENTS/settings", response_class=HTMLResponse)
async def pages_dispatch(
    request: Request,
    page: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    accounts = list_accounts(db)
    path = request.url.path
    last_seen = datetime.now(tz=timezone.utc).isoformat()
    template_map = {
        "/AGENTS/accounts": "partials/page_accounts.html",
        "/AGENTS/post": "partials/page_post.html",
        "/AGENTS/3d": "partials/page_3d.html",
        "/AGENTS/settings": "partials/page_settings.html",
    }
    content_template = template_map.get(path, "partials/page_timeline.html")
    posts, has_next, safe_page, safe_limit = _paginate_posts(db, page, limit)
    context = {
        "request": request,
        "accounts": accounts,
        "posts": posts,
        "last_seen": last_seen,
        "page": safe_page,
        "limit": safe_limit,
        "has_next": has_next,
        "title": "Timeline",
        "subtitle": "Latest first",
        "content_template": content_template,
    }
    if request.headers.get("HX-Request") == "true":
        return templates.TemplateResponse(content_template, context)
    return templates.TemplateResponse("index.html", context)


@router.get("/AGENTS/account/{account_id}", response_class=HTMLResponse)
async def account_posts_page(
    request: Request,
    account_id: int,
    page: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    accounts = list_accounts(db)
    account = db.get(Account, account_id)
    if not account:
        return templates.TemplateResponse(
            "partials/page_settings.html", {"request": request}
        )
    posts, has_next, safe_page, safe_limit = _paginate_posts(
        db, page, limit, account_id=account_id
    )
    last_seen = datetime.now(tz=timezone.utc).isoformat()
    context = {
        "request": request,
        "accounts": accounts,
        "account": account,
        "posts": posts,
        "last_seen": last_seen,
        "page": safe_page,
        "limit": safe_limit,
        "has_next": has_next,
        "account_id": account_id,
        "title": f"{account.name} Timeline",
        "subtitle": "Account posts",
        "content_template": "partials/page_account_posts.html",
    }
    if request.headers.get("HX-Request") == "true":
        return templates.TemplateResponse("partials/page_account_posts.html", context)
    return templates.TemplateResponse("index.html", context)


@router.get("/AGENTS/timeline", response_class=HTMLResponse)
@router.get("/partials/timeline", response_class=HTMLResponse)
async def timeline_partial(
    request: Request,
    page: int = 1,
    limit: int = 50,
    account_id: int | None = None,
    db: Session = Depends(get_db),
):
    posts, has_next, safe_page, safe_limit = _paginate_posts(
        db, page, limit, account_id=account_id
    )
    last_seen = datetime.now(tz=timezone.utc).isoformat()
    title = "Timeline"
    subtitle = "Latest first"
    if account_id is not None:
        account = db.get(Account, account_id)
        if account:
            title = f"{account.name} Timeline"
            subtitle = "Account posts"
    return templates.TemplateResponse(
        "partials/timeline.html",
        {
            "request": request,
            "posts": posts,
            "last_seen": last_seen,
            "page": safe_page,
            "limit": safe_limit,
            "has_next": has_next,
            "account_id": account_id,
            "title": title,
            "subtitle": subtitle,
        },
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
    human_text: str = Form(""),
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
        human_text=human_text[:280],
        goal=goal,
        result_summary=result_summary,
        tags_csv=tags_csv,
    )
    create_post(db, post)
    posts, has_next, safe_page, safe_limit = _paginate_posts(db, 1, 50)
    last_seen = datetime.now(tz=timezone.utc).isoformat()
    return templates.TemplateResponse(
        "partials/page_timeline.html",
        {
            "request": request,
            "posts": posts,
            "last_seen": last_seen,
            "page": safe_page,
            "limit": safe_limit,
            "has_next": has_next,
            "title": "Timeline",
            "subtitle": "Latest first",
        },
    )


@router.post("/posts/{post_id}/delete", response_class=HTMLResponse)
async def delete_post_form(
    request: Request,
    post_id: int,
    page: int = 1,
    limit: int = 50,
    account_id: int | None = None,
    db: Session = Depends(get_db),
):
    post = get_post(db, post_id)
    if post:
        delete_post(db, post)
    posts, has_next, safe_page, safe_limit = _paginate_posts(
        db, page, limit, account_id=account_id
    )
    last_seen = datetime.now(tz=timezone.utc).isoformat()
    title = "Timeline"
    subtitle = "Latest first"
    if account_id is not None:
        account = db.get(Account, account_id)
        if account:
            title = f"{account.name} Timeline"
            subtitle = "Account posts"
    return templates.TemplateResponse(
        "partials/timeline.html",
        {
            "request": request,
            "posts": posts,
            "last_seen": last_seen,
            "page": safe_page,
            "limit": safe_limit,
            "has_next": has_next,
            "account_id": account_id,
            "title": title,
            "subtitle": subtitle,
        },
    )
