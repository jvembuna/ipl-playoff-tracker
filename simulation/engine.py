from __future__ import annotations

import random
from collections.abc import Iterable
from collections import Counter

from ipl_data.models import Match, StandingRow
from simulation.models import SimulationResult, TeamState


class MonteCarloSimulator:
    def __init__(self, seed: int | None = None) -> None:
        self.random = random.Random(seed)

    def run(
        self,
        standings: list[StandingRow],
        remaining_matches: list[Match],
        match_probabilities: dict[str, dict[str, float]] | None,
        simulation_count: int,
    ) -> SimulationResult:
        normalized_probabilities = self._normalize_match_probabilities(
            remaining_matches, match_probabilities
        )
        qualification_counts: Counter[str] = Counter()

        for _ in range(simulation_count):
            team_states = {
                row.team_id: TeamState.from_standing(row)
                for row in standings
            }
            """
            Each simulation is one possible way the season could finish.
            For every remaining match, we sample one winner from the configured
            probability. Running many simulations lets the qualification percentages
            emerge from the aggregate results.
            """
            for match in remaining_matches:
                probability_team_a = normalized_probabilities[match.match_id]
                if self.random.random() <= probability_team_a:
                    winner = team_states[match.team_a]
                    loser = team_states[match.team_b]
                else:
                    winner = team_states[match.team_b]
                    loser = team_states[match.team_a]

                self._apply_result(winner=winner, loser=loser)

            for team_id in self._qualified_team_ids(team_states.values()):
                qualification_counts[team_id] += 1

        percentages = {
            row.team_id: (qualification_counts[row.team_id] / simulation_count) * 100
            for row in standings
        }
        return SimulationResult(
            qualification_percentages=percentages,
            match_probabilities=normalized_probabilities,
        )

    def _apply_result(self, winner: TeamState, loser: TeamState) -> None:
        winner.played += 1
        winner.won += 1
        winner.points += 2

        loser.played += 1
        loser.lost += 1

    def _normalize_match_probabilities(
        self,
        remaining_matches: Iterable[Match],
        raw_probabilities: dict[str, dict[str, float]] | None,
    ) -> dict[str, float]:
        raw_probabilities = raw_probabilities or {}
        normalized: dict[str, float] = {}

        for match in remaining_matches:
            probability = raw_probabilities.get(match.match_id, {}).get(
                "team_a_win_probability", 0.5
            )
            normalized[match.match_id] = min(1.0, max(0.0, probability))

        return normalized

    def _qualified_team_ids(self, teams: Iterable[TeamState]) -> list[str]:
        ranked = self._rank_teams(teams)
        return [team.team_id for team in ranked[:4]]

    def _rank_teams(self, teams: Iterable[TeamState]) -> list[TeamState]:
        return sorted(
            teams,
            key=lambda team: (team.points, team.net_run_rate, team.team_id),
            reverse=True,
        )
