from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass(frozen=True)
class StandingRow:
    team_id: str
    team_name: str
    played: int
    won: int
    lost: int
    no_result: int
    points: int
    net_run_rate: float

    def to_dict(self) -> dict[str, object]:
        return {
            "team_id": self.team_id,
            "team_name": self.team_name,
            "played": self.played,
            "won": self.won,
            "lost": self.lost,
            "no_result": self.no_result,
            "points": self.points,
            "net_run_rate": round(self.net_run_rate, 3),
        }


@dataclass(frozen=True)
class Match:
    match_id: str
    team_a: str
    team_b: str
    status: str = "upcoming"
    source_metadata: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        data = {
            "match_id": self.match_id,
            "team_a": self.team_a,
            "team_b": self.team_b,
            "status": self.status,
        }
        if self.source_metadata:
            data["source_metadata"] = self.source_metadata
        return data


@dataclass(frozen=True)
class ResultsSnapshot:
    standings: list[StandingRow]
    completed_match_ids: set[str]
    source_name: str
    refreshed_at: str


@dataclass(frozen=True)
class AppState:
    standings: list[StandingRow]
    full_fixture_list: list[Match]
    remaining_matches: list[Match]
    source_name: str
    refreshed_at: str
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "standings": [row.to_dict() for row in self.standings],
            "full_fixture_list": [match.to_dict() for match in self.full_fixture_list],
            "remaining_matches": [match.to_dict() for match in self.remaining_matches],
            "source_name": self.source_name,
            "refreshed_at": self.refreshed_at,
            "notes": self.notes,
        }
