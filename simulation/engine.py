from __future__ import annotations

import random
from collections import Counter

from ipl_data.models import Match, StandingRow
from simulation.models import SimulationResult, TeamState
from simulation.probability import normalize_match_probabilities
from simulation.qualification import qualified_team_ids


class MonteCarloSimulator:
    def __init__(self, nrr_delta: float = 0.1, seed: int | None = None) -> None:
        self.nrr_delta = nrr_delta
        self.random = random.Random(seed)

    def run(
        self,
        standings: list[StandingRow],
        remaining_matches: list[Match],
        match_probabilities: dict[str, object] | None,
        simulation_count: int,
    ) -> SimulationResult:
        normalized_probabilities = normalize_match_probabilities(
            remaining_matches, match_probabilities
        )
        qualification_counts: Counter[str] = Counter()

        for _ in range(simulation_count):
            team_states = {
                row.team_id: TeamState.from_standing(row)
                for row in standings
            }

            for match in remaining_matches:
                probability_team_a = normalized_probabilities[match.match_id]
                if self.random.random() <= probability_team_a:
                    winner = team_states[match.team_a]
                    loser = team_states[match.team_b]
                else:
                    winner = team_states[match.team_b]
                    loser = team_states[match.team_a]

                self._apply_result(winner=winner, loser=loser)

            for team_id in qualified_team_ids(team_states.values()):
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
        winner.net_run_rate += self.nrr_delta

        loser.played += 1
        loser.lost += 1
        loser.net_run_rate -= self.nrr_delta
