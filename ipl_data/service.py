from __future__ import annotations

from collections.abc import Iterable

from ipl_data.fixture_provider import FixtureStateProvider
from ipl_data.models import AppState, Match, ResultsSnapshot, StandingRow, utc_now_iso
from ipl_data.providers.results_provider import NDTVResultsProvider
from ipl_data.providers.schedule_provider import NDTVScheduleProvider
from ipl_data.state_store import InMemoryStateStore


class IPLDataService:
    def __init__(
        self,
        state_store: InMemoryStateStore,
        fixture_provider: FixtureStateProvider,
        schedule_provider: NDTVScheduleProvider | None = None,
        results_provider: NDTVResultsProvider | None = None,
    ) -> None:
        self.state_store = state_store
        self.fixture_provider = fixture_provider
        self.schedule_provider = schedule_provider or NDTVScheduleProvider()
        self.results_provider = results_provider or NDTVResultsProvider()

    def get_state(self) -> AppState:
        return self.state_store.get_state()

    def refresh_data(self) -> AppState:
        existing_state = self.state_store.get_state()

        try:
            full_schedule = self._load_or_refresh_schedule(existing_state.full_fixture_list)
            snapshot = self.results_provider.load_snapshot()
            refreshed_state = self._merge_schedule_and_snapshot(full_schedule, snapshot)
        except Exception as exc:
            refreshed_state = self.fixture_provider.load_state()
            refreshed_state = AppState(
                standings=refreshed_state.standings,
                full_fixture_list=refreshed_state.full_fixture_list,
                remaining_matches=refreshed_state.remaining_matches,
                source_name=refreshed_state.source_name,
                refreshed_at=utc_now_iso(),
                notes=refreshed_state.notes
                + [f"Live refresh failed; using fixture fallback: {exc!s}"],
            )

        self.state_store.set_state(refreshed_state)
        return refreshed_state

    def _load_or_refresh_schedule(self, current_schedule: list[Match]) -> list[Match]:
        if current_schedule:
            return current_schedule
        try:
            return self.schedule_provider.load_schedule()
        except Exception:
            return self.fixture_provider.load_state().full_fixture_list

    def _merge_schedule_and_snapshot(
        self, full_schedule: list[Match], snapshot: ResultsSnapshot
    ) -> AppState:
        completed_ids = snapshot.completed_match_ids
        merged_schedule = []
        for match in full_schedule:
            if match.match_id in completed_ids:
                status = "completed"
            else:
                status = "upcoming"
            merged_schedule.append(
                Match(
                    match_id=match.match_id,
                    team_a=match.team_a,
                    team_b=match.team_b,
                    status=status,
                    source_metadata=match.source_metadata,
                )
            )

        remaining_matches = [match for match in merged_schedule if match.status == "upcoming"]
        standings = sorted(
            snapshot.standings,
            key=lambda row: (row.points, row.net_run_rate, row.team_id),
            reverse=True,
        )
        return AppState(
            standings=standings,
            full_fixture_list=merged_schedule,
            remaining_matches=remaining_matches,
            source_name=snapshot.source_name,
            refreshed_at=snapshot.refreshed_at,
            notes=[
                "Season schedule is stored in memory and reused across refreshes.",
                "Refresh updates the daily-changing standings/results snapshot.",
            ],
        )

    @staticmethod
    def derive_remaining_matches(
        full_schedule: Iterable[Match], completed_match_ids: set[str]
    ) -> list[Match]:
        return [
            match
            for match in full_schedule
            if match.match_id not in completed_match_ids and match.status != "completed"
        ]
