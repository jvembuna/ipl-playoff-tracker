from __future__ import annotations

from ipl_data.models import AppState
from ipl_data.state_store import InMemoryStateStore


class IPLDataService:
    def __init__(self, state_store: InMemoryStateStore) -> None:
        self.state_store = state_store

    def get_state(self) -> AppState:
        return self.state_store.get_state()
