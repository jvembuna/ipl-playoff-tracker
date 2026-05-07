# Specification

## Product Summary

Build a simple IPL 2026 playoff tracker using Flask, plain HTML, plain CSS, and plain JavaScript.

The app estimates each team's chance of finishing in the top 4 based on:

- the current standings snapshot
- the remaining matches
- default or user-adjusted per-match win probabilities

## What The App Does Today

### Current State

The app currently uses fixture-backed data rather than live refresh.

It reads:

- current standings and remaining matches from [ipl_2026_sample.json](/Users/janardhanan/Desktop/learning/codex-drills/ipl/ipl_data/fixtures/ipl_2026_sample.json)
- saved history from [ipl_2026_qualification_history.json](/Users/janardhanan/Desktop/learning/codex-drills/ipl/ipl_data/fixtures/ipl_2026_qualification_history.json)

### Simulation Input

The user can:

- accept the default 50/50 assumptions
- move one slider per remaining match
- choose a simulation count, bounded by the server

### Simulation Output

The app returns:

- qualification percentages by team
- normalized match probabilities
- standings ordered like a league table using points and NRR

### History

The app shows a line chart of qualification history over time.

Each history point represents a daily baseline run using:

- that day's standings
- that day's remaining fixtures
- default 50/50 win probabilities

History persistence is opt-in and development-only.

## API Contract

### `GET /`

Renders the main page.

### `GET /api/state`

Returns:

```json
{
  "status": "ok",
  "default_simulations": 10000,
  "max_simulations": 50000,
  "state": {
    "standings": [],
    "remaining_matches": [],
    "qualification_history": [],
    "source_name": "fixture",
    "refreshed_at": "2026-04-29",
    "notes": []
  }
}
```

### `POST /api/simulate`

Request:

```json
{
  "simulation_count": 10000,
  "match_probabilities": {
    "match_041": {
      "team_a_win_probability": 0.5
    }
  }
}
```

Response:

```json
{
  "status": "ok",
  "simulation_count": 10000,
  "qualification_percentages": {
    "PBKS": 92.4,
    "RCB": 85.1
  },
  "ordered_standings": [],
  "match_probabilities": {
    "match_041": 0.5
  }
}
```

The backend clamps the simulation count to a safe maximum.

## Domain Model

### Standing Row

Fields:

- `team_id`
- `team_name`
- `played`
- `won`
- `lost`
- `no_result`
- `points`
- `net_run_rate`

### Match

Fields:

- `match_id`
- `team_a`
- `team_b`

### Qualification History Entry

Fields:

- `date`
- `simulation_count`
- `qualification_percentages`

### App State

Fields:

- `standings`
- `remaining_matches`
- `qualification_history`
- `source_name`
- `refreshed_at`
- `notes`

## Simulation Rules

### Qualification

- Top 4 teams qualify

### Match Outcome

- Each remaining match is sampled independently
- Default win probability is `0.5`
- User adjustments are set directly per remaining match

### Points

- Winner gets 2 points
- No-result rows from the current standings are preserved
- Future no-results are not simulated

### Tie-Break

The current ranking uses:

1. higher points
2. higher NRR
3. deterministic fallback by `team_id`

This is still a simplification, but it is closer to the real league table than a pure alphabetical fallback.

### Simulated NRR Movement

Future simulated matches also move NRR.

For a decided match:

- sample a small positive delta from a normal distribution
- winner gets `+delta`
- loser gets `-delta`

Current default parameters:

- mean `0.10`
- standard deviation `0.03`
- minimum delta `0.01`

This is a simulation heuristic, not an official scorecard-based NRR recomputation from runs and overs.

## Current UX

The UI shows:

- a standings table with team logos and qualification chance
- a remaining matches panel with one slider per match
- a qualification history line chart below the standings table
- a clickable legend that highlights one team and mutes the rest
- a no-more-matches state that disables simulation controls once the schedule is finished

On first load, the frontend automatically runs the default simulation.

## Known Simplifications

- shared in-memory state for all users
- fixture-backed data only
- manual JSON updates for new standings and fixtures
- no database
- no auth
- no background jobs
- no live refresh endpoint
- no future no-result simulation
- simulated future NRR uses a simple random delta model rather than official cumulative score-based recomputation

## Deployment Assumptions

- local development runs through Flask
- production runs in a Docker container with `gunicorn`
- AWS App Runner is the current deployment target
- history persistence stays disabled in production

## Extension Points

- reintroduce live standings refresh later
- add a scheduler or database later
- improve tie-break logic later
- add richer history views later
- add match history or calibration later
