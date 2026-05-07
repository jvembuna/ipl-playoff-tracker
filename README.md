# IPL 2026 Playoff Tracker

## Overview

This is a small Flask web app that estimates IPL 2026 playoff qualification chances with a Monte Carlo simulation.

The app currently uses manually maintained JSON fixtures for:

- the latest standings snapshot
- the remaining match list
- daily qualification history

Users can adjust the win probability for each remaining match, run the simulation, and see:

- qualification chance in the standings table
- a qualification history chart over time
- remaining matches with per-match sliders

The app also uses:

- points as the main ranking metric
- NRR as the tie-break when teams are level on points
- a small simulated NRR movement for future wins and losses

## Current Product Shape

The current version is intentionally simple:

- Flask backend
- plain HTML, CSS, and JavaScript frontend
- shared in-memory server state
- fixture-backed IPL data
- no database
- no live data refresh flow

The standings table includes team logos, points, no-result count, and qualification chance.

## How It Works

1. The backend loads the current state from [ipl_2026_sample.json](/Users/janardhanan/Desktop/learning/codex-drills/ipl/ipl_data/fixtures/ipl_2026_sample.json).
2. It loads saved history from [ipl_2026_qualification_history.json](/Users/janardhanan/Desktop/learning/codex-drills/ipl/ipl_data/fixtures/ipl_2026_qualification_history.json).
3. The frontend loads the current state from `GET /api/state`.
4. On page load, the frontend runs a default simulation.
5. Users can adjust per-match probabilities and rerun the simulation through `POST /api/simulate`.

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
flask --app app run
```

Or run directly:

```bash
python app.py
```

## History Persistence In Dev

The app can record one baseline history snapshot per `refreshed_at` date, but only when explicitly enabled.

Enable it locally with:

```bash
export APP_ENV=development
export ENABLE_HISTORY_PERSIST=true
flask --app app run
```

Behavior:

- only the baseline 50/50 simulation is persisted
- custom slider experiments are not persisted
- a given `refreshed_at` date is written at most once

## Deployment

The project includes a container deployment path for AWS App Runner:

- [Dockerfile](/Users/janardhanan/Desktop/learning/codex-drills/ipl/Dockerfile)
- [.dockerignore](/Users/janardhanan/Desktop/learning/codex-drills/ipl/.dockerignore)
- [deploy/apprunner-service.json](/Users/janardhanan/Desktop/learning/codex-drills/ipl/deploy/apprunner-service.json)

The production container:

- serves the Flask app with `gunicorn`
- respects the platform `PORT` environment variable
- disables history persistence by default

## Key Endpoints

- `GET /`
- `GET /api/state`
- `POST /api/simulate`

## Repository Documents

- [SPEC.md](/Users/janardhanan/Desktop/learning/codex-drills/ipl/SPEC.md)
- [ARCHITECTURE.md](/Users/janardhanan/Desktop/learning/codex-drills/ipl/ARCHITECTURE.md)
- [MONTE_CARLO.md](/Users/janardhanan/Desktop/learning/codex-drills/ipl/MONTE_CARLO.md)
- [AGENTS.md](/Users/janardhanan/Desktop/learning/codex-drills/ipl/AGENTS.md)
- [TODO.md](/Users/janardhanan/Desktop/learning/codex-drills/ipl/TODO.md)
