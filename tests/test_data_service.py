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


def test_seeded_standings_max_matches_played_is_14() -> None:
    fixture_provider = FixtureStateProvider()
    state = fixture_provider.load_state()

    for row in state.standings:
        assert row.played <= 14


def test_seeded_standings_points_match_record() -> None:
    fixture_provider = FixtureStateProvider()
    state = fixture_provider.load_state()

    for row in state.standings:
        assert row.points == (2 * row.won) + row.no_result


def test_seeded_standings_played_matches_record() -> None:
    fixture_provider = FixtureStateProvider()
    state = fixture_provider.load_state()

    for row in state.standings:
        assert row.played == row.won + row.lost + row.no_result
