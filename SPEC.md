# Specification

## Product Summary

Build a simple IPL 2026 qualification probability web app using Flask, plain HTML, plain CSS, and plain JavaScript.

The app estimates each team's probability of qualification based on:

- current standings
- remaining matches
- default or user-adjusted win probabilities

This is an intentional evolution of an earlier notebook implementation that exhaustively enumerated remaining outcomes for a small set of matches. The web app will preserve the same domain logic where useful, but package it into maintainable modules and replace exhaustive branching with Monte Carlo simulation.

## Core Features

### 1. Standings And Fixtures State

The app maintains one shared in-memory state for all users in the first version.

That state contains:

- current standings
- static season fixture list
- remaining fixtures derived from schedule minus completed results
- metadata about source and last refresh time

### 2. Manual Data Refresh

The UI provides a `Refresh IPL Data` button.

When clicked:

- the frontend calls the backend refresh endpoint
- the backend attempts to fetch the latest IPL 2026 standings or results snapshot
- the backend merges that refreshed state with the stored season fixture list
- remaining matches are recalculated from the known completed results
- if live retrieval fails, the backend can load local JSON fixture data
- the in-memory application state is updated

### 3. Simulation Inputs

The user can run a Monte Carlo simulation using:

- default 50/50 remaining match probabilities, or
- adjusted probabilities set directly per remaining match with sliders

The first version should keep the input model understandable and bounded.

### 4. Qualification Simulation

The backend runs a Monte Carlo simulation over the remaining matches.

For each trial:

- start from the current standings
- simulate each remaining match using configured probabilities
- update points
- rank teams using simplified qualification rules
- count which teams qualify

After all trials:

- convert counts into qualification percentages
- return results to the frontend

This differs from the 2024 notebook, which recursively explored both winner paths for every remaining match. That approach works for a tiny search space, but Monte Carlo is the right default once custom probabilities and a larger schedule are involved.

### 5. Results Display

The UI displays:

- current standings with qualification chance included in the same table
- remaining matches
- one slider per remaining match
- qualification percentages sorted from highest to lowest
- a simple inline visual bar beside each qualification percentage

Team logos may be shown if cleanly available, but logos are optional for the first functional version.

## API Contract

### `GET /`

Renders the main page.

### `POST /api/refresh-data`

Refreshes shared IPL state.

Planned response shape:

```json
{
  "status": "ok",
  "source": "live|fixture",
  "refreshed_at": "ISO-8601 timestamp",
  "standings": [],
  "remaining_matches": []
}
```

### `GET /api/state`

Returns the currently loaded in-memory application state.

### `POST /api/simulate`

Accepts simulation settings and returns qualification results.

Planned request shape:

```json
{
  "simulation_count": 10000,
  "match_probabilities": {
    "match_001": {
      "team_a_win_probability": 0.5
    },
    "match_002": {
      "team_a_win_probability": 0.5
    }
  }
}
```

Planned response shape:

```json
{
  "status": "ok",
  "simulation_count": 10000,
  "qualification_percentages": {
    "CSK": 62.3,
    "MI": 48.9
  }
}
```

The backend must enforce a safe maximum simulation count even if the client requests more.

## Domain Model

### Standing Row

Planned fields:

- team_id
- team_name
- played
- won
- lost
- no_result
- points
- net_run_rate

### Match

Planned fields:

- match_id
- team_a
- team_b
- status
- optional source metadata

### App State

Planned fields:

- standings
- full_fixture_list
- remaining_matches
- source_name
- refreshed_at

## Simulation Rules For V1

The first version will use a simplified qualification model.

### Qualification

- Assume top 4 teams qualify

### Match Outcome

- Each remaining match is simulated with a Bernoulli draw
- Default win probability is 50/50
- User adjustments are set directly per remaining match

### Points

- Winner gets 2 points
- No-result handling is not simulated initially unless already present in the source data

### Tie-Break

Start with a simple isolated tie-break strategy:

1. higher points
2. higher net run rate if available
3. stable deterministic fallback such as team name or team id

This keeps the ranking deterministic while allowing future refinement.

### Net Run Rate Handling

The notebook updated NRR using a placeholder rule where a winner gained `+0.1` and the loser lost `-0.1` for each simulated future match.

For V1, we will keep that placeholder approach on purpose because it is simple, deterministic, and gives the simulator a practical tie-break mechanism without modeling match margins in detail.

The V1 policy is:

- use refreshed NRR as the starting tie-break value
- apply a fixed simulated delta of `+0.1` to the winner and `-0.1` to the loser for each simulated future match
- keep the policy in one module so it can later be improved without touching routes or UI code

This is a simplification, not a claim of realistic NRR modeling.

## Known Simplifications

- Shared in-memory state for all users
- Manual refresh only
- One competition only: IPL 2026
- Simplified tie-break behavior
- The schedule can be captured once and stored locally rather than re-fetched every refresh
- Manual refresh updates daily-changing standings/results data only
- Local JSON fallback may be the primary development path if live data is unreliable
- Simulated NRR movement uses a fixed `+0.1/-0.1` placeholder rule in V1

## Extension Points

- Replace the data source without changing the rest of the app
- Add scheduled refresh later
- Swap in a database later
- Add richer tie-break logic later
- Add per-match editing later
- Add historical calibration or team form models later
