from __future__ import annotations

import json
from pathlib import Path

from ipl_data.models import AppState, Match, StandingRow


class FixtureStateProvider:
    def __init__(self, fixture_path: Path | None = None) -> None:
        default_path = Path(__file__).resolve().parent / "fixtures" / "ipl_2026_sample.json"
        self.fixture_path = fixture_path or default_path

    def load_state(self) -> AppState:
        payload = json.loads(self.fixture_path.read_text())
        standings = [
            StandingRow(
                team_id=row["team_id"],
                team_name=row["team_name"],
                played=row["played"],
                won=row["won"],
                lost=row["lost"],
                no_result=row["no_result"],
                points=row["points"],
            )
            for row in payload["standings"]
        ]
        remaining_matches = [
            Match(
                match_id=match["match_id"],
                team_a=match["team_a"],
                team_b=match["team_b"],
            )
            for match in payload["remaining_matches"]
        ]
        return AppState(
            standings=sorted(
                standings,
                key=lambda row: (row.points, row.team_id),
                reverse=True,
            ),
            remaining_matches=remaining_matches,
            source_name=payload.get("source_name", "fixture"),
            refreshed_at=payload["refreshed_at"],
            notes=payload.get("notes", []),
        )
