from __future__ import annotations

import re

import requests
from bs4 import BeautifulSoup

from ipl_data.models import Match
from ipl_data.providers.base import ScheduleProvider


TEAM_NAME_TO_ID = {
    "Chennai Super Kings": "CSK",
    "Delhi Capitals": "DC",
    "Gujarat Titans": "GT",
    "Kolkata Knight Riders": "KKR",
    "Lucknow Super Giants": "LSG",
    "Mumbai Indians": "MI",
    "Punjab Kings": "PBKS",
    "Rajasthan Royals": "RR",
    "Royal Challengers Bengaluru": "RCB",
    "Sunrisers Hyderabad": "SRH",
}


class NDTVScheduleProvider(ScheduleProvider):
    SCHEDULE_URL = "https://sports.ndtv.com/ipl-2026/schedules-fixtures"

    def load_schedule(self) -> list[Match]:
        response = requests.get(self.SCHEDULE_URL, timeout=15)
        response.raise_for_status()
        return parse_schedule_html(response.text)


def parse_schedule_html(html: str) -> list[Match]:
    soup = BeautifulSoup(html, "html.parser")
    lines = [line.strip() for line in soup.get_text("\n").splitlines() if line.strip()]

    matches: list[Match] = []
    seen_ids: set[str] = set()
    pattern = re.compile(
        r"(?P<prefix>Recent|Upcoming)?\s*"
        r"(?P<team_a>[A-Za-z ]+?)\s+vs\s+(?P<team_b>[A-Za-z ]+?)\s+"
        r"Match\s+(?P<match_number>\d+),\s*Indian Premier League,\s*2026(?P<rest>.*)",
    )

    for line in lines:
        if " vs " not in line or "Indian Premier League, 2026" not in line:
            continue
        matched = pattern.search(" ".join(line.split()))
        if not matched:
            continue

        team_a_name = matched.group("team_a").strip()
        team_b_name = matched.group("team_b").strip()
        team_a = TEAM_NAME_TO_ID.get(team_a_name)
        team_b = TEAM_NAME_TO_ID.get(team_b_name)
        if not team_a or not team_b:
            continue

        match_id = f"match_{int(matched.group('match_number')):03d}"
        if match_id in seen_ids:
            continue

        rest = matched.group("rest")
        if "Match Ended" in rest or "beat" in rest or "tied with" in rest:
            status = "completed"
        elif "Match Abandoned" in rest or "Abandoned" in rest:
            status = "completed"
        else:
            status = "upcoming"

        matches.append(
            Match(
                match_id=match_id,
                team_a=team_a,
                team_b=team_b,
                status=status,
                source_metadata={
                    "team_a_name": team_a_name,
                    "team_b_name": team_b_name,
                },
            )
        )
        seen_ids.add(match_id)

    if not matches:
        raise ValueError("Could not parse schedule from NDTV HTML")
    return sorted(matches, key=lambda item: item.match_id)
