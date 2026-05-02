from __future__ import annotations

import json
from pathlib import Path

from ipl_data.fixture_provider import FixtureStateProvider
from ipl_data.history_store import QualificationHistoryStore


def test_history_store_records_one_snapshot_per_date(tmp_path: Path) -> None:
    fixture_path = tmp_path / "sample.json"
    history_path = tmp_path / "history.json"
    fixture_path.write_text(
        json.dumps(
            {
                "source_name": "manual_seed",
                "refreshed_at": "2026-04-29",
                "notes": [],
                "standings": [
                    {
                        "team_id": "CSK",
                        "team_name": "CSK",
                        "played": 8,
                        "won": 3,
                        "lost": 5,
                        "no_result": 0,
                        "points": 6,
                        "net_run_rate": 0.005,
                    },
                    {
                        "team_id": "MI",
                        "team_name": "MI",
                        "played": 7,
                        "won": 2,
                        "lost": 5,
                        "no_result": 0,
                        "points": 4,
                        "net_run_rate": -0.803,
                    },
                ],
                "remaining_matches": [
                    {"match_id": "match_001", "team_a": "CSK", "team_b": "MI"}
                ],
            }
        )
    )
    history_path.write_text(json.dumps({"qualification_history": []}))

    provider = FixtureStateProvider(fixture_path=fixture_path, history_path=history_path)
    history_store = QualificationHistoryStore(fixture_provider=provider)
    state = provider.load_state()

    updated_state = history_store.maybe_record_daily_snapshot(
        state=state,
        qualification_percentages={"CSK": 65.4, "MI": 34.6},
        simulation_count=10000,
    )
    second_state = history_store.maybe_record_daily_snapshot(
        state=updated_state,
        qualification_percentages={"CSK": 70.0, "MI": 30.0},
        simulation_count=10000,
    )

    assert len(updated_state.qualification_history) == 1
    assert len(second_state.qualification_history) == 1
    assert second_state.qualification_history[0].qualification_percentages["CSK"] == 65.4
