from __future__ import annotations

from ipl_data.models import Match
from simulation.probability import normalize_match_probabilities


def test_probability_defaults_to_fifty_fifty() -> None:
    matches = [Match(match_id="match_001", team_a="CSK", team_b="MI", status="upcoming")]
    normalized = normalize_match_probabilities(matches, {})
    assert normalized == {"match_001": 0.5}


def test_probability_is_clamped() -> None:
    matches = [
        Match(match_id="match_001", team_a="CSK", team_b="MI", status="upcoming"),
        Match(match_id="match_002", team_a="RCB", team_b="GT", status="upcoming"),
    ]
    normalized = normalize_match_probabilities(
        matches,
        {
            "match_001": {"team_a_win_probability": 1.8},
            "match_002": {"team_a_win_probability": -0.2},
        },
    )
    assert normalized["match_001"] == 1.0
    assert normalized["match_002"] == 0.0
