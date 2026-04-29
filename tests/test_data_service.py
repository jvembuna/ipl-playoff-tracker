from __future__ import annotations

from ipl_data.fixture_provider import FixtureStateProvider
from ipl_data.service import IPLDataService
from ipl_data.state_store import InMemoryStateStore


def test_data_service_returns_seeded_state() -> None:
    store = InMemoryStateStore()
    fixture_provider = FixtureStateProvider()
    seeded = fixture_provider.load_state()
    store.set_state(seeded)
    service = IPLDataService(state_store=store, fixture_provider=fixture_provider)

    state = service.get_state()
    assert state.source_name == "manual_seed"
    assert len(state.standings) == 10
    assert len(state.remaining_matches) == 30


def test_fixture_provider_uses_points_only_ordering() -> None:
    state = FixtureStateProvider().load_state()
    assert state.standings[0].team_id == "PBKS"
    assert state.standings[-1].team_id in {"LSG", "MI"}
