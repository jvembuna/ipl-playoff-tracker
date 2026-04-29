from __future__ import annotations

from simulation.models import TeamState
from simulation.qualification import qualified_team_ids, rank_teams


def test_rank_teams_uses_points_then_nrr() -> None:
    teams = [
        TeamState("CSK", 10, 6, 4, 0, 12),
        TeamState("MI", 10, 6, 4, 0, 12),
        TeamState("RCB", 10, 7, 3, 0, 14),
    ]

    ranked = rank_teams(teams)
    assert [team.team_id for team in ranked] == ["RCB", "MI", "CSK"]


def test_qualified_team_ids_returns_top_four() -> None:
    teams = [
        TeamState("A", 0, 0, 0, 0, 10),
        TeamState("B", 0, 0, 0, 0, 9),
        TeamState("C", 0, 0, 0, 0, 8),
        TeamState("D", 0, 0, 0, 0, 7),
        TeamState("E", 0, 0, 0, 0, 6),
    ]
    assert qualified_team_ids(teams) == ["A", "B", "C", "D"]
