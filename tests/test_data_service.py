from __future__ import annotations

from ipl_data.fixture_provider import FixtureStateProvider
from ipl_data.models import AppState, Match, ResultsSnapshot, StandingRow
from ipl_data.service import IPLDataService
from ipl_data.state_store import InMemoryStateStore


class StubScheduleProvider:
    def load_schedule(self) -> list[Match]:
        return [
            Match(match_id="match_001", team_a="CSK", team_b="MI", status="upcoming"),
            Match(match_id="match_002", team_a="RCB", team_b="GT", status="upcoming"),
        ]


class StubResultsProvider:
    def load_snapshot(self) -> ResultsSnapshot:
        return ResultsSnapshot(
            standings=[
                StandingRow("CSK", "CSK", 10, 6, 4, 0, 12, 0.4),
                StandingRow("MI", "MI", 10, 5, 5, 0, 10, 0.1),
                StandingRow("RCB", "RCB", 10, 6, 4, 0, 12, 0.8),
                StandingRow("GT", "GT", 10, 4, 6, 0, 8, -0.2),
            ],
            completed_match_ids={"match_001"},
            source_name="stub_live",
            refreshed_at="2026-04-28T20:00:00+00:00",
        )


def test_refresh_derives_remaining_matches() -> None:
    store = InMemoryStateStore()
    fixture_provider = FixtureStateProvider()
    store.set_state(fixture_provider.load_state())

    service = IPLDataService(
        state_store=store,
        fixture_provider=fixture_provider,
        schedule_provider=StubScheduleProvider(),
        results_provider=StubResultsProvider(),
    )

    state = service._merge_schedule_and_snapshot(
        StubScheduleProvider().load_schedule(),
        StubResultsProvider().load_snapshot(),
    )

    assert len(state.remaining_matches) == 1
    assert state.remaining_matches[0].match_id == "match_002"


def test_fixture_fallback_keeps_app_usable() -> None:
    store = InMemoryStateStore()
    fixture_provider = FixtureStateProvider()
    original_state = fixture_provider.load_state()
    store.set_state(original_state)

    class BrokenResultsProvider:
        def load_snapshot(self) -> ResultsSnapshot:
            raise RuntimeError("boom")

    service = IPLDataService(
        state_store=store,
        fixture_provider=fixture_provider,
        schedule_provider=StubScheduleProvider(),
        results_provider=BrokenResultsProvider(),
    )

    refreshed = service.refresh_data()
    assert refreshed.source_name == "fixture_sample"
    assert refreshed.remaining_matches
    assert any("fallback" in note.lower() for note in refreshed.notes)
