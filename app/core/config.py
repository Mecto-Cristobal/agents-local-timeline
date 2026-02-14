from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = os.getenv("AGENTS_DB_PATH", str(DATA_DIR / "agents.db"))
DB_URL = f"sqlite:///{DB_PATH}"

APP_TITLE = "AGENTS"
APP_DESCRIPTION = "Local-only agents timeline. Do not expose to the internet."
WSL_QUEUE_PATH = DATA_DIR / "wsl_post_queue.ndjson"
