@echo off
setlocal

if not exist .venv (
  python -m venv .venv
)

call .venv\Scripts\activate
pip install -r requirements.txt
if errorlevel 1 exit /b %errorlevel%
alembic upgrade head
if errorlevel 1 exit /b %errorlevel%
uvicorn app.main:app --host 127.0.0.1 --port 20000
