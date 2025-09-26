"""Thread-safe stop signal (placeholder)."""

from __future__ import annotations

import threading


class StopSignal:
    def __init__(self) -> None:
        self._event = threading.Event()

    def stop(self) -> None:
        self._event.set()

    def is_set(self) -> bool:
        return self._event.is_set()
