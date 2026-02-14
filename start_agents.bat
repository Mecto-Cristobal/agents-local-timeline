@echo off
setlocal
chcp 65001 >nul
set PYTHONUTF8=1
if "%AGENTS_HOST%"=="" set AGENTS_HOST=0.0.0.0
if "%AGENTS_PORT%"=="" set AGENTS_PORT=20000

if not exist .venv (
  python -m venv .venv
)

call .venv\Scripts\activate
pip install -r requirements.txt
if errorlevel 1 exit /b %errorlevel%
alembic upgrade head
if errorlevel 1 exit /b %errorlevel%
uvicorn app.main:app --host %AGENTS_HOST% --port %AGENTS_PORT%
