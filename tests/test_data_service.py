from __future__ import annotations

from ipl_data.fixture_provider import FixtureStateProvider
from ipl_data.service import IPLDataService
from ipl_data.state_store import InMemoryStateStore


def test_data_service_returns_seeded_state() -> None:
    store = InMemoryStateStore()
    fixture_provider = FixtureStateProvider()
    seeded = fixture_provider.load_state()
    store.set_state(seeded)
    service = IPLDataService(state_store=store)

    state = service.get_state()
    assert state.source_name == "manual_seed"
    assert len(state.standings) == 10
    assert state.standings[1].team_id == "RCB"
    assert state.standings[1].net_run_rate == 1.420
