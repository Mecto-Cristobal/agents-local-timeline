from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class EventPayload:
    event: str
    data: dict
    created_at: datetime


class Broadcaster:
    def __init__(self) -> None:
        self._subscribers: set[asyncio.Queue[EventPayload]] = set()

    def subscribe(self) -> asyncio.Queue[EventPayload]:
        queue: asyncio.Queue[EventPayload] = asyncio.Queue()
        self._subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[EventPayload]) -> None:
        self._subscribers.discard(queue)

    async def publish(self, payload: EventPayload) -> None:
        for queue in list(self._subscribers):
            await queue.put(payload)
