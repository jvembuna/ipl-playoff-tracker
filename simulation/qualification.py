from __future__ import annotations

from collections.abc import Iterable

from simulation.models import TeamState


QUALIFICATION_SLOTS = 4


def rank_teams(teams: Iterable[TeamState]) -> list[TeamState]:
    return sorted(
        teams,
        key=lambda team: (team.points, team.team_id),
        reverse=True,
    )


def qualified_team_ids(teams: Iterable[TeamState]) -> list[str]:
    ranked = rank_teams(teams)
    return [team.team_id for team in ranked[:QUALIFICATION_SLOTS]]
