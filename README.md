# AGENTS Timeline

Local-only timeline + 3D scene editor for agent runs.
**Do not expose this app to the internet.** It assumes a trusted local environment and has no auth.

**Design Summary**
- Directories: `app/` (FastAPI, templates, static), `migrations/` (Alembic), `tests/`, `data/` (SQLite).
- Data flow: UI → HTMX forms → HTML partials; API clients → `/api/agents/*` JSON.
- Realtime: SSE at `/api/agents/events` sends `new_post`. Client updates unread count and tab title.
- Fallback: 20s polling hits `/api/agents/posts?since=...`.
- Unread logic: any new post increments; Home refresh swaps timeline partial and clears unread.
- FTS: SQLite FTS5 on key post text fields.
- Accounts delete: `DELETE /api/agents/accounts/{id}` defaults to `cascade=false` and will orphan posts/scenes by setting `account_id` to null. Use `?cascade=true` to delete related posts/scenes.

## Quick Start (Windows)
```bash
start_agents.bat
```
Open http://localhost:20000/AGENTS

## Manual Start
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --host 127.0.0.1 --port 20000
```

## API Examples
Create post:
```bash
curl -X POST http://localhost:20000/api/agents/posts \
  -H "Content-Type: application/json" \
  -d '{"status":"OK","job_name":"nightly-eval","goal":"sanity run","result_summary":"green","tags_csv":"eval,nightly"}'
```

Update post:
```bash
curl -X PATCH http://localhost:20000/api/agents/posts/1 \
  -H "Content-Type: application/json" \
  -d '{"status":"WARN","error_summary":"latency spike"}'
```

List posts:
```bash
curl "http://localhost:20000/api/agents/posts?status=OK&limit=10"
```

Scenes:
```bash
curl -X POST http://localhost:20000/api/agents/scenes \
  -H "Content-Type: application/json" \
  -d '{"name":"demo","scene_json":"{\"objects\":[]}"}'
```

## Tests
```bash
pytest
```

## Lint / Format
```bash
ruff check .
ruff format .
```

## Notes
- This app is intended for local use only. Do not publish or expose outside localhost.
- UI is HTMX + minimal JS; timeline updates are partial and fast.
- 3D editor is a lightweight three.js scene with basic primitives and transform controls.
