#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import socket
import sys
import urllib.error
import urllib.request
from pathlib import Path


def _build_bases(port: str) -> list[str]:
    bases: list[str] = []
    base_url = os.getenv("AGENTS_BASE_URL")
    if base_url:
        bases.append(base_url)
    host_ip = os.getenv("AGENTS_HOST_IP")
    if host_ip:
        bases.append(f"http://{host_ip}:{port}")
    bases.extend([f"http://127.0.0.1:{port}", f"http://localhost:{port}"])
    try:
        with open("/etc/resolv.conf", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("nameserver "):
                    ns = line.split()[1].strip()
                    if ns:
                        bases.append(f"http://{ns}:{port}")
                    break
    except OSError:
        pass
    return bases


def _is_reachable(base: str, timeout: float = 3.0) -> bool:
    req = urllib.request.Request(f"{base}/", method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout):
            return True
    except (urllib.error.URLError, socket.timeout):
        return False


def _post_json(url: str, payload: dict, timeout: float = 3.0) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    with urllib.request.urlopen(req, timeout=timeout):
        return


def main() -> int:
    status = sys.argv[1] if len(sys.argv) > 1 else "OK"
    text = sys.argv[2] if len(sys.argv) > 2 else "Codex progress update"
    summary = sys.argv[3] if len(sys.argv) > 3 else ""
    tags = sys.argv[4] if len(sys.argv) > 4 else "system,progress,codex"
    port = os.getenv("AGENTS_PORT", "20000")
    queue_file = Path(os.getenv("AGENTS_QUEUE_FILE", "data/wsl_post_queue.ndjson"))

    payload = {
        "status": status,
        "job_name": "codex-run",
        "human_text": text,
        "result_summary": summary,
        "tags_csv": tags,
    }

    for base in _build_bases(port):
        if not _is_reachable(base):
            continue
        try:
            _post_json(f"{base}/api/agents/system/progress", payload)
            print(f"posted_to={base}")
            return 0
        except (urllib.error.URLError, socket.timeout):
            continue

    queue_file.parent.mkdir(parents=True, exist_ok=True)
    with queue_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    print(f"queued_to={queue_file.as_posix()}")
    print(f"reason=no reachable AGENTS endpoint on port {port}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
