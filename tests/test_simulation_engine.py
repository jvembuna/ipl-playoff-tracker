from __future__ import annotations

from ipl_data.models import Match, StandingRow
from simulation.engine import MonteCarloSimulator
from simulation.models import TeamState


def test_forced_match_probability_drives_result() -> None:
    simulator = MonteCarloSimulator(seed=7)
    standings = [
        StandingRow("CSK", "CSK", 10, 6, 4, 0, 12, 0.320),
        StandingRow("MI", "MI", 10, 5, 5, 0, 10, -0.180),
        StandingRow("RCB", "RCB", 10, 7, 3, 0, 14, 0.900),
        StandingRow("GT", "GT", 10, 4, 6, 0, 8, -0.510),
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
        StandingRow("CSK", "CSK", 10, 6, 4, 0, 12, 0.320),
        StandingRow("MI", "MI", 10, 5, 5, 0, 10, -0.180),
        StandingRow("RCB", "RCB", 10, 7, 3, 0, 14, 0.900),
        StandingRow("GT", "GT", 10, 4, 6, 0, 8, -0.510),
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
        TeamState("CSK", 10, 6, 4, 0, 12, 0.005),
        TeamState("MI", 10, 6, 4, 0, 12, 0.104),
        TeamState("RCB", 10, 7, 3, 0, 14, 0.500),
    ]

    ranked = simulator._rank_teams(teams)
    assert [team.team_id for team in ranked] == ["RCB", "MI", "CSK"]


def test_qualified_team_ids_returns_top_four() -> None:
    simulator = MonteCarloSimulator(seed=1)
    teams = [
        TeamState("A", 0, 0, 0, 0, 10, 0.1),
        TeamState("B", 0, 0, 0, 0, 9, 0.1),
        TeamState("C", 0, 0, 0, 0, 8, 0.1),
        TeamState("D", 0, 0, 0, 0, 7, 0.1),
        TeamState("E", 0, 0, 0, 0, 6, 0.1),
    ]

    assert simulator._qualified_team_ids(teams) == ["A", "B", "C", "D"]


def test_nrr_delta_is_positive_and_bounded() -> None:
    simulator = MonteCarloSimulator(seed=1)

    deltas = [simulator._sample_nrr_delta() for _ in range(50)]

    assert all(delta >= simulator.NRR_DELTA_MIN for delta in deltas)


def test_apply_result_updates_points_and_nrr() -> None:
    simulator = MonteCarloSimulator(seed=1)
    winner = TeamState("CSK", 10, 6, 4, 0, 12, 0.200)
    loser = TeamState("MI", 10, 5, 5, 0, 10, -0.150)

    simulator._apply_result(winner=winner, loser=loser)

    assert winner.played == 11
    assert winner.won == 7
    assert winner.points == 14
    assert winner.net_run_rate > 0.200

    assert loser.played == 11
    assert loser.lost == 6
    assert loser.points == 10
    assert loser.net_run_rate < -0.150


def test_empty_remaining_matches_returns_current_top_four() -> None:
    simulator = MonteCarloSimulator(seed=1)
    standings = [
        StandingRow("SRH", "SRH", 11, 7, 4, 0, 14, 0.737),
        StandingRow("PBKS", "PBKS", 10, 6, 3, 1, 13, 0.571),
        StandingRow("RCB", "RCB", 9, 6, 3, 0, 12, 1.420),
        StandingRow("RR", "RR", 10, 6, 4, 0, 12, 0.510),
        StandingRow("GT", "GT", 10, 6, 4, 0, 12, -0.147),
    ]

    result = simulator.run(
        standings=standings,
        remaining_matches=[],
        match_probabilities={},
        simulation_count=100,
    )

    assert result.qualification_percentages["SRH"] == 100.0
    assert result.qualification_percentages["PBKS"] == 100.0
    assert result.qualification_percentages["RCB"] == 100.0
    assert result.qualification_percentages["RR"] == 100.0
    assert result.qualification_percentages["GT"] == 0.0
