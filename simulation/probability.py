from __future__ import annotations

from collections.abc import Iterable

from ipl_data.models import Match


def normalize_match_probabilities(
    remaining_matches: Iterable[Match], raw_probabilities: dict[str, object] | None
) -> dict[str, float]:
    raw_probabilities = raw_probabilities or {}
    normalized: dict[str, float] = {}

    for match in remaining_matches:
        payload = raw_probabilities.get(match.match_id, {})
        probability = 0.5
        if isinstance(payload, dict):
            candidate = payload.get("team_a_win_probability", 0.5)
        else:
            candidate = payload

        try:
            probability = float(candidate)
        except (TypeError, ValueError):
            probability = 0.5

        normalized[match.match_id] = min(1.0, max(0.0, probability))

    return normalized
