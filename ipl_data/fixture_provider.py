from __future__ import annotations

import json
from pathlib import Path

from ipl_data.models import AppState, Match, QualificationHistoryEntry, StandingRow


class FixtureStateProvider:
    def __init__(
        self,
        fixture_path: Path | None = None,
        history_path: Path | None = None,
    ) -> None:
        default_path = Path(__file__).resolve().parent / "fixtures" / "ipl_2026_sample.json"
        default_history_path = (
            Path(__file__).resolve().parent / "fixtures" / "ipl_2026_qualification_history.json"
        )
        self.fixture_path = fixture_path or default_path
        self.history_path = history_path or default_history_path

    def load_state(self) -> AppState:
        payload = self.load_payload()
        history_payload = self.load_history_payload()
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
        qualification_history = [
            QualificationHistoryEntry(
                date=entry["date"],
                simulation_count=entry["simulation_count"],
                qualification_percentages={
                    team_id: float(value)
                    for team_id, value in entry["qualification_percentages"].items()
                },
            )
            for entry in history_payload.get("qualification_history", [])
        ]
        return AppState(
            standings=sorted(
                standings,
                key=lambda row: (row.points, row.team_id),
                reverse=True,
            ),
            remaining_matches=remaining_matches,
            qualification_history=qualification_history,
            source_name=payload.get("source_name", "fixture"),
            refreshed_at=payload["refreshed_at"],
            notes=payload.get("notes", []),
        )

    def load_payload(self) -> dict[str, object]:
        return json.loads(self.fixture_path.read_text())

    def load_history_payload(self) -> dict[str, object]:
        if not self.history_path.exists():
            return {"qualification_history": []}
        return json.loads(self.history_path.read_text())

    def save_payload(self, payload: dict[str, object]) -> None:
        self.fixture_path.write_text(format_seed_json(payload))

    def save_history_payload(self, payload: dict[str, object]) -> None:
        self.history_path.write_text(format_history_json(payload))


def format_seed_json(payload: dict[str, object]) -> str:
    lines = [
        "{",
        f'  "source_name": {json.dumps(payload["source_name"])},',
        f'  "refreshed_at": {json.dumps(payload["refreshed_at"])},',
        '  "notes": [',
    ]

    notes = payload.get("notes", [])
    for index, note in enumerate(notes):
        suffix = "," if index < len(notes) - 1 else ""
        lines.append(f"    {json.dumps(note)}{suffix}")
    lines.append("  ],")

    lines.append('  "standings": [')
    standings = payload.get("standings", [])
    for index, row in enumerate(standings):
        suffix = "," if index < len(standings) - 1 else ""
        lines.append(f"    {json.dumps(row, separators=(', ', ': '))}{suffix}")
    lines.append("  ],")

    lines.append('  "remaining_matches": [')
    matches = payload.get("remaining_matches", [])
    for index, match in enumerate(matches):
        suffix = "," if index < len(matches) - 1 else ""
        lines.append(f"    {json.dumps(match, separators=(', ', ': '))}{suffix}")
    lines.append("  ]")
    lines.append("}")
    return "\n".join(lines) + "\n"


def format_history_json(payload: dict[str, object]) -> str:
    lines = ["{", '  "qualification_history": [']
    history = payload.get("qualification_history", [])
    for index, entry in enumerate(history):
        suffix = "," if index < len(history) - 1 else ""
        lines.append(f"    {json.dumps(entry, separators=(', ', ': '))}{suffix}")
    lines.append("  ]")
    lines.append("}")
    return "\n".join(lines) + "\n"
