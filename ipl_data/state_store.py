from __future__ import annotations

from threading import Lock

from ipl_data.models import AppState


class InMemoryStateStore:
    def __init__(self) -> None:
        self._state: AppState | None = None
        self._lock = Lock()

    def get_state(self) -> AppState:
        with self._lock:
            if self._state is None:
                raise RuntimeError("IPL state has not been initialized")
            return self._state

    def set_state(self, state: AppState) -> None:
        with self._lock:
            self._state = state
