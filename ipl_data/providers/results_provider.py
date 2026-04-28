from __future__ import annotations

import re

import requests
from bs4 import BeautifulSoup

from ipl_data.models import ResultsSnapshot, StandingRow, utc_now_iso
from ipl_data.providers.base import ResultsProvider


class NDTVResultsProvider(ResultsProvider):
    POINTS_TABLE_URL = "https://sports.ndtv.com/ipl-2026/points-table"
    SCHEDULE_URL = "https://sports.ndtv.com/ipl-2026/schedules-fixtures"

    def load_snapshot(self) -> ResultsSnapshot:
        points_response = requests.get(self.POINTS_TABLE_URL, timeout=15)
        points_response.raise_for_status()
        standings = parse_points_table_html(points_response.text)

        schedule_response = requests.get(self.SCHEDULE_URL, timeout=15)
        schedule_response.raise_for_status()
        completed_match_ids = parse_completed_match_ids(schedule_response.text)

        return ResultsSnapshot(
            standings=standings,
            completed_match_ids=completed_match_ids,
            source_name="ndtv_live",
            refreshed_at=utc_now_iso(),
        )


def parse_points_table_html(html: str) -> list[StandingRow]:
    soup = BeautifulSoup(html, "html.parser")
    table = None
    for candidate in soup.find_all("table"):
        header_text = " ".join(
            cell.get_text(" ", strip=True).upper() for cell in candidate.find_all("th")
        )
        if "NRR" in header_text and "PTS" in header_text and "TEAMS" in header_text:
            table = candidate
            break

    if table is None:
        standings = _parse_points_table_from_lines(soup.get_text("\n"))
        if not standings:
            raise ValueError("Could not locate IPL points table")
        return standings

    standings: list[StandingRow] = []
    for row in table.find_all("tr")[1:]:
        cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["td", "th"])]
        if len(cells) < 8:
            continue

        team_token = cells[1]
        team_id = team_token.split()[-1].upper()
        played = int(cells[2])
        won = int(cells[3])
        lost = int(cells[4])
        no_result = int(cells[6])
        points = int(cells[7])
        nrr = float(cells[8])
        standings.append(
            StandingRow(
                team_id=team_id,
                team_name=team_id,
                played=played,
                won=won,
                lost=lost,
                no_result=no_result,
                points=points,
                net_run_rate=nrr,
            )
        )

    if not standings:
        raise ValueError("Could not parse standings rows from points table")
    return standings


def _parse_points_table_from_lines(text: str) -> list[StandingRow]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    standings: list[StandingRow] = []
    team_pattern = re.compile(r"^[A-Z]{2,4}$")

    for index, line in enumerate(lines):
        if not line.isdigit():
            continue
        if index + 8 >= len(lines):
            continue
        team_id_candidate = lines[index + 2].strip().upper()
        if not team_pattern.match(team_id_candidate):
            continue
        try:
            played = int(lines[index + 3])
            won = int(lines[index + 4])
            lost = int(lines[index + 5])
            no_result = int(lines[index + 7])
            points = int(lines[index + 8])
            nrr = float(lines[index + 9])
        except (IndexError, ValueError):
            continue
        standings.append(
            StandingRow(
                team_id=team_id_candidate,
                team_name=team_id_candidate,
                played=played,
                won=won,
                lost=lost,
                no_result=no_result,
                points=points,
                net_run_rate=nrr,
            )
        )
    return standings


def parse_completed_match_ids(html: str) -> set[str]:
    soup = BeautifulSoup(html, "html.parser")
    lines = [line.strip() for line in soup.get_text("\n").splitlines() if line.strip()]
    completed: set[str] = set()
    pattern = re.compile(r"Match\s+(?P<match_number>\d+),\s*Indian Premier League,\s*2026")

    for line in lines:
        if "Match " not in line or "Indian Premier League, 2026" not in line:
            continue
        matched = pattern.search(line)
        if not matched:
            continue
        if "Match Ended" in line or "Match Abandoned" in line or "beat" in line or "tied with" in line:
            completed.add(f"match_{int(matched.group('match_number')):03d}")
    return completed
