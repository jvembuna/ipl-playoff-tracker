from __future__ import annotations

from ipl_data.fixture_provider import FixtureStateProvider
from ipl_data.models import AppState


class QualificationHistoryStore:
    def __init__(self, fixture_provider: FixtureStateProvider) -> None:
        self.fixture_provider = fixture_provider

    def maybe_record_daily_snapshot(
        self,
        state: AppState,
        qualification_percentages: dict[str, float],
        simulation_count: int,
    ) -> AppState:
        payload = self.fixture_provider.load_history_payload()
        history = payload.setdefault("qualification_history", [])

        if any(entry.get("date") == state.refreshed_at for entry in history):
            return self.fixture_provider.load_state()

        history.append(
            {
                "date": state.refreshed_at,
                "simulation_count": simulation_count,
                "qualification_percentages": {
                    team_id: round(value, 1)
                    for team_id, value in qualification_percentages.items()
                },
            }
        )
        self.fixture_provider.save_history_payload(payload)
        return self.fixture_provider.load_state()
