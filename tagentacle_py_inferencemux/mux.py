"""InferenceMux: Controls when to infer — IDLE/BUSY state machine + followup queue.

When IDLE and triggered, starts an inference cycle.
When BUSY and triggered, queues the signal for followup after the current cycle.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from enum import Enum
from typing import Any


class MuxState(str, Enum):
    IDLE = "idle"
    BUSY = "busy"


@dataclass
class TriggerSignal:
    """Reason for triggering inference."""

    topic: str = ""
    detail: Any = None


class InferenceMux:
    """IDLE/BUSY state machine with followup queue.

    Usage::

        mux = InferenceMux()

        async def on_bus_message(topic, msg):
            if inbox.push(topic, msg):
                await mux.trigger(TriggerSignal(topic=topic))

        # In main loop:
        async for signal in mux:
            messages = inbox.drain()
            # ... run inference ...
            mux.release()
    """

    def __init__(self) -> None:
        self._state = MuxState.IDLE
        self._followup: list[TriggerSignal] = []
        self._current: TriggerSignal | None = None
        self._event = asyncio.Event()

    @property
    def state(self) -> MuxState:
        return self._state

    async def trigger(self, signal: TriggerSignal | None = None) -> None:
        """Request an inference cycle.

        If IDLE, signals immediately. If BUSY, appends to followup queue.
        """
        sig = signal or TriggerSignal()
        if self._state == MuxState.IDLE:
            self._state = MuxState.BUSY
            self._current = sig
            self._event.set()
        else:
            self._followup.append(sig)

    def release(self) -> None:
        """Mark current inference cycle as done.

        If followup queue is non-empty, immediately re-trigger.
        """
        self._current = None
        if self._followup:
            self._current = self._followup.pop(0)
            self._event.set()
        else:
            self._state = MuxState.IDLE
            self._event.clear()

    async def wait(self) -> TriggerSignal:
        """Wait for the next trigger signal. Blocks until triggered."""
        await self._event.wait()
        self._event.clear()
        self._state = MuxState.BUSY
        return self._current or TriggerSignal()

    @property
    def has_followup(self) -> bool:
        """True if there are queued followup triggers."""
        return len(self._followup) > 0
