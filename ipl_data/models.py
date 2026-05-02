from __future__ import annotations

from dataclasses import dataclass, field


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
            "net_run_rate": self.net_run_rate,
        }


@dataclass(frozen=True)
class Match:
    match_id: str
    team_a: str
    team_b: str

    def to_dict(self) -> dict[str, object]:
        return {
            "match_id": self.match_id,
            "team_a": self.team_a,
            "team_b": self.team_b,
        }


@dataclass(frozen=True)
class QualificationHistoryEntry:
    date: str
    simulation_count: int
    qualification_percentages: dict[str, float]

    def to_dict(self) -> dict[str, object]:
        return {
            "date": self.date,
            "simulation_count": self.simulation_count,
            "qualification_percentages": {
                team_id: round(value, 1)
                for team_id, value in self.qualification_percentages.items()
            },
        }


@dataclass(frozen=True)
class AppState:
    standings: list[StandingRow]
    remaining_matches: list[Match]
    qualification_history: list[QualificationHistoryEntry]
    source_name: str
    refreshed_at: str
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "standings": [row.to_dict() for row in self.standings],
            "remaining_matches": [match.to_dict() for match in self.remaining_matches],
            "qualification_history": [entry.to_dict() for entry in self.qualification_history],
            "source_name": self.source_name,
            "refreshed_at": self.refreshed_at,
            "notes": self.notes,
        }
