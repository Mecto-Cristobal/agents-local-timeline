#!/usr/bin/env bash
set -euo pipefail

STATUS="${1:-OK}"
TEXT="${2:-Codex progress update}"
SUMMARY="${3:-}"
TAGS="${4:-system,progress,codex}"
PORT="${AGENTS_PORT:-20000}"
QUEUE_FILE="${AGENTS_QUEUE_FILE:-data/wsl_post_queue.ndjson}"

payload="{\"status\":\"${STATUS}\",\"job_name\":\"codex-run\",\"human_text\":\"${TEXT}\",\"result_summary\":\"${SUMMARY}\",\"tags_csv\":\"${TAGS}\"}"

# Priority: explicit URL > explicit host > local fallbacks > WSL nameserver fallback.
declare -a bases=()
if [[ -n "${AGENTS_BASE_URL:-}" ]]; then
  bases+=("${AGENTS_BASE_URL}")
fi
if [[ -n "${AGENTS_HOST_IP:-}" ]]; then
  bases+=("http://${AGENTS_HOST_IP}:${PORT}")
fi
bases+=("http://127.0.0.1:${PORT}" "http://localhost:${PORT}")

if [[ -r /etc/resolv.conf ]]; then
  ns="$(awk '/^nameserver/{print $2; exit}' /etc/resolv.conf || true)"
  if [[ -n "${ns}" ]]; then
    bases+=("http://${ns}:${PORT}")
  fi
fi

for base in "${bases[@]}"; do
  if curl -sS --max-time 3 -o /dev/null "${base}/"; then
    curl -sS -X POST "${base}/api/agents/system/progress" \
      -H "Content-Type: application/json" \
      -d "${payload}"
    echo
    echo "posted_to=${base}"
    exit 0
  fi
done

mkdir -p "$(dirname "${QUEUE_FILE}")"
printf '%s\n' "${payload}" >> "${QUEUE_FILE}"
echo "queued_to=${QUEUE_FILE}"
echo "reason=no reachable AGENTS endpoint on port ${PORT}"
exit 0
