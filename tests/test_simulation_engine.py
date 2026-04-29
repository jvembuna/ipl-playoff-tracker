from __future__ import annotations

from ipl_data.models import Match, StandingRow
from simulation.engine import MonteCarloSimulator
from simulation.models import TeamState


def test_forced_match_probability_drives_result() -> None:
    simulator = MonteCarloSimulator(seed=7)
    standings = [
        StandingRow("CSK", "CSK", 10, 6, 4, 0, 12),
        StandingRow("MI", "MI", 10, 5, 5, 0, 10),
        StandingRow("RCB", "RCB", 10, 7, 3, 0, 14),
        StandingRow("GT", "GT", 10, 4, 6, 0, 8),
    ]
    matches = [Match(match_id="match_001", team_a="CSK", team_b="MI")]

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
        StandingRow("CSK", "CSK", 10, 6, 4, 0, 12),
        StandingRow("MI", "MI", 10, 5, 5, 0, 10),
        StandingRow("RCB", "RCB", 10, 7, 3, 0, 14),
        StandingRow("GT", "GT", 10, 4, 6, 0, 8),
    ]
    original_points = standings[0].points

    simulator.run(
        standings=standings,
        remaining_matches=[Match(match_id="match_001", team_a="CSK", team_b="MI")],
        match_probabilities={},
        simulation_count=5,
    )

    assert standings[0].points == original_points


def test_probability_defaults_to_fifty_fifty() -> None:
    simulator = MonteCarloSimulator(seed=1)
    matches = [Match(match_id="match_001", team_a="CSK", team_b="MI")]

    normalized = simulator._normalize_match_probabilities(matches, {})

    assert normalized == {"match_001": 0.5}


def test_probability_is_clamped() -> None:
    simulator = MonteCarloSimulator(seed=1)
    matches = [
        Match(match_id="match_001", team_a="CSK", team_b="MI"),
        Match(match_id="match_002", team_a="RCB", team_b="GT"),
    ]

    normalized = simulator._normalize_match_probabilities(
        matches,
        {
            "match_001": {"team_a_win_probability": 1.8},
            "match_002": {"team_a_win_probability": -0.2},
        },
    )

    assert normalized["match_001"] == 1.0
    assert normalized["match_002"] == 0.0


def test_rank_teams_uses_points_then_team_id() -> None:
    simulator = MonteCarloSimulator(seed=1)
    teams = [
        TeamState("CSK", 10, 6, 4, 0, 12),
        TeamState("MI", 10, 6, 4, 0, 12),
        TeamState("RCB", 10, 7, 3, 0, 14),
    ]

    ranked = simulator._rank_teams(teams)
    assert [team.team_id for team in ranked] == ["RCB", "MI", "CSK"]


def test_qualified_team_ids_returns_top_four() -> None:
    simulator = MonteCarloSimulator(seed=1)
    teams = [
        TeamState("A", 0, 0, 0, 0, 10),
        TeamState("B", 0, 0, 0, 0, 9),
        TeamState("C", 0, 0, 0, 0, 8),
        TeamState("D", 0, 0, 0, 0, 7),
        TeamState("E", 0, 0, 0, 0, 6),
    ]

    assert simulator._qualified_team_ids(teams) == ["A", "B", "C", "D"]
