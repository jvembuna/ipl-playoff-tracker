# IPL 2026 Qualification Probability Web App

## Overview

This project will recreate a simple IPL qualification probability calculator as a small web app for the 2026 season.

The starting reference is a 2024 Jupyter Notebook that already established the core idea:

- represent teams using matches played, points, and net run rate
- represent remaining fixtures as team-vs-team pairs
- rank teams by points and then NRR
- estimate top-4 qualification odds from simulated remaining results

The new project keeps that basic mental model, but moves it into cleaner modules with a web interface, tests, and a safer simulation design.

The app will:

- fetch or load current IPL standings and remaining fixtures
- let the user refresh the shared in-memory dataset
- let the user adjust per-match win probabilities
- run a Monte Carlo simulation on the backend
- show each team's estimated chance of finishing in the top qualification spots

This repository is intentionally planned in two phases:

1. Phase 0: documentation, design, and implementation plan
2. Phase 1: application code after plan approval

No application code should be added until the plan in this repository is approved.

## Goals

- Keep the first version simple, readable, and easy to run locally
- Use Flask on the backend
- Use plain HTML, CSS, and JavaScript on the frontend
- Keep scraping and simulation logic isolated behind small interfaces
- Allow fallback to local JSON data if live data fetching is brittle
- Make the simulation engine independently testable

## Non-Goals For V1

- No database
- No authentication
- No background scheduler
- No distributed cache
- No heavy frontend framework
- No attempt to exactly mirror every official IPL tie-break rule in the first version

## Planned Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
flask --app app run
```

## Planned User Flow

1. Open the web app
2. View the current standings table with qualification chance included
3. Click `Refresh IPL Data` to load the latest available standings/results snapshot
4. Adjust the win-probability slider for each remaining match if desired
5. Click `Run Simulation`
6. View the standings table re-ordered from highest to lowest qualification chance

## Planned Data Sources

The app will treat season data as two different concerns:

- static schedule data: fetched once from a practical web source and stored in Python or a local fixture file
- refreshable standings/results data: updated from the web as new match results become known

For the first version, remaining matches do not need to be re-fetched on every click if the season schedule has already been captured cleanly. The daily-changing part is the standings/results snapshot, which the user will refresh manually from the UI for now.

If live fetching is unreliable, blocked, or too brittle, the app will fall back to local JSON fixtures. The rest of the app should behave the same regardless of data source.

## Repository Documents

- [SPEC.md](/Users/janardhanan/Desktop/learning/codex-drills/ipl/SPEC.md)
- [ARCHITECTURE.md](/Users/janardhanan/Desktop/learning/codex-drills/ipl/ARCHITECTURE.md)
- [AGENTS.md](/Users/janardhanan/Desktop/learning/codex-drills/ipl/AGENTS.md)
- [TODO.md](/Users/janardhanan/Desktop/learning/codex-drills/ipl/TODO.md)
