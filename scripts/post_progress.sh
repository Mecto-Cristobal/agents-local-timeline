#!/usr/bin/env bash
set -euo pipefail

STATUS="${1:-OK}"
TEXT="${2:-Codex progress update}"
SUMMARY="${3:-}"
TAGS="${4:-system,progress,codex}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if command -v python3 >/dev/null 2>&1; then
  exec python3 "${SCRIPT_DIR}/post_progress.py" "${STATUS}" "${TEXT}" "${SUMMARY}" "${TAGS}"
fi
exec python "${SCRIPT_DIR}/post_progress.py" "${STATUS}" "${TEXT}" "${SUMMARY}" "${TAGS}"
