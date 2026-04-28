from __future__ import annotations

from ipl_data.models import Match, StandingRow
from simulation.engine import MonteCarloSimulator


def test_forced_match_probability_drives_result() -> None:
    simulator = MonteCarloSimulator(seed=7)
    standings = [
        StandingRow("CSK", "CSK", 10, 6, 4, 0, 12, 0.1),
        StandingRow("MI", "MI", 10, 5, 5, 0, 10, 0.1),
        StandingRow("RCB", "RCB", 10, 7, 3, 0, 14, 0.2),
        StandingRow("GT", "GT", 10, 4, 6, 0, 8, 0.0),
    ]
    matches = [Match(match_id="match_001", team_a="CSK", team_b="MI", status="upcoming")]

    result = simulator.run(
        standings=standings,
        remaining_matches=matches,
        match_probabilities={"match_001": {"team_a_win_probability": 1.0}},
        simulation_count=20,
    )

    assert result.match_probabilities["match_001"] == 1.0
    assert result.qualification_percentages["CSK"] == 100.0


def test_simulation_preserves_input_standings() -> None:
    simulator = MonteCarloSimulator(seed=3)
    standings = [
        StandingRow("CSK", "CSK", 10, 6, 4, 0, 12, 0.1),
        StandingRow("MI", "MI", 10, 5, 5, 0, 10, 0.1),
        StandingRow("RCB", "RCB", 10, 7, 3, 0, 14, 0.2),
        StandingRow("GT", "GT", 10, 4, 6, 0, 8, 0.0),
    ]
    original_points = standings[0].points

    simulator.run(
        standings=standings,
        remaining_matches=[Match(match_id="match_001", team_a="CSK", team_b="MI", status="upcoming")],
        match_probabilities={},
        simulation_count=5,
    )

    assert standings[0].points == original_points
