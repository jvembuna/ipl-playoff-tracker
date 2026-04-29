from __future__ import annotations

from dataclasses import dataclass

from ipl_data.models import Match, StandingRow


@dataclass
class TeamState:
    team_id: str
    played: int
    won: int
    lost: int
    no_result: int
    points: int

    @classmethod
    def from_standing(cls, row: StandingRow) -> "TeamState":
        return cls(
            team_id=row.team_id,
            played=row.played,
            won=row.won,
            lost=row.lost,
            no_result=row.no_result,
            points=row.points,
        )


@dataclass(frozen=True)
class SimulationResult:
    qualification_percentages: dict[str, float]
    match_probabilities: dict[str, float]
