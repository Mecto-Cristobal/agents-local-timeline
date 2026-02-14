from __future__ import annotations

import asyncio
from datetime import datetime

import orjson
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/api/agents", tags=["events"])


@router.get("/events")
async def events(request: Request):
    broadcaster = request.app.state.broadcaster
    queue = broadcaster.subscribe()

    async def event_stream():
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    payload = await asyncio.wait_for(queue.get(), timeout=15)
                    data = orjson.dumps(payload.data).decode("utf-8")
                    yield f"event: {payload.event}\n"
                    yield f"data: {data}\n\n"
                except asyncio.TimeoutError:
                    yield "event: heartbeat\n"
                    yield f"data: {datetime.utcnow().isoformat()}\n\n"
        finally:
            broadcaster.unsubscribe(queue)

    return StreamingResponse(event_stream(), media_type="text/event-stream")
