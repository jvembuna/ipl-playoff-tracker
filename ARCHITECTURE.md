# Architecture

## Design Intent

The codebase is intentionally small and explicit:

- Flask handles HTTP and template rendering
- `ipl_data` owns fixture loading and history persistence
- `simulation` owns Monte Carlo logic
- the frontend renders state and sends simple API requests

The current app is optimized for clarity over abstraction depth.

## Current High-Level Flow

```text
Browser
  -> GET /
  -> Render HTML + CSS + JS

Frontend startup
  -> GET /api/state
  -> render standings, matches, history
  -> POST /api/simulate with default settings
  -> render qualification chances

User action: Run Simulation
  -> POST /api/simulate
  -> Flask route
  -> Monte Carlo simulator
  -> JSON response
  -> frontend rerenders standings and chart
```

## Current Module Boundaries

### Flask Layer

Primary file:

- [app.py](/Users/janardhanan/Desktop/learning/codex-drills/ipl/app.py)

Responsibilities:

- create the app
- read environment configuration
- wire together fixture provider, history store, state store, and simulator
- expose routes
- clamp simulation count

Routes:

- `GET /`
- `GET /api/state`
- `POST /api/simulate`

### `ipl_data` Layer

Primary files:

- [ipl_data/models.py](/Users/janardhanan/Desktop/learning/codex-drills/ipl/ipl_data/models.py)
- [ipl_data/fixture_provider.py](/Users/janardhanan/Desktop/learning/codex-drills/ipl/ipl_data/fixture_provider.py)
- [ipl_data/history_store.py](/Users/janardhanan/Desktop/learning/codex-drills/ipl/ipl_data/history_store.py)
- [ipl_data/service.py](/Users/janardhanan/Desktop/learning/codex-drills/ipl/ipl_data/service.py)
- [ipl_data/state_store.py](/Users/janardhanan/Desktop/learning/codex-drills/ipl/ipl_data/state_store.py)

Responsibilities:

- define standings, match, history, and app-state models
- load current snapshot from the seed file
- load history from the history file
- format JSON output in one-line-per-entity style
- optionally append one daily baseline history snapshot in development mode
- expose current state through a small service boundary

### `simulation` Layer

Primary files:

- [simulation/models.py](/Users/janardhanan/Desktop/learning/codex-drills/ipl/simulation/models.py)
- [simulation/engine.py](/Users/janardhanan/Desktop/learning/codex-drills/ipl/simulation/engine.py)

Responsibilities:

- convert standing rows into mutable per-trial team state
- normalize per-match probabilities
- run Monte Carlo trials
- apply results to copied state
- move NRR on simulated wins and losses using a small sampled delta
- rank teams by points, then NRR, then deterministic team id fallback
- return qualification percentages and normalized probabilities

### Frontend Layer

Primary files:

- [templates/index.html](/Users/janardhanan/Desktop/learning/codex-drills/ipl/templates/index.html)
- [static/js/app.js](/Users/janardhanan/Desktop/learning/codex-drills/ipl/static/js/app.js)
- [static/css/styles.css](/Users/janardhanan/Desktop/learning/codex-drills/ipl/static/css/styles.css)

Responsibilities:

- render standings with logos and qualification chance
- render remaining matches and sliders
- auto-run the default simulation on first load
- render the qualification history chart
- highlight one team at a time from the clickable legend
- disable simulation controls when there are no remaining matches

## State Management

The server stores one shared in-memory `AppState`.

Source of truth at startup:

- seed snapshot: [ipl_2026_sample.json](/Users/janardhanan/Desktop/learning/codex-drills/ipl/ipl_data/fixtures/ipl_2026_sample.json)
- history file: [ipl_2026_qualification_history.json](/Users/janardhanan/Desktop/learning/codex-drills/ipl/ipl_data/fixtures/ipl_2026_qualification_history.json)

Implications:

- all users see the same state
- state resets on process restart
- manual fixture edits are the current workflow

## History Persistence Flow

This flow is enabled only when:

- `APP_ENV=development`
- `ENABLE_HISTORY_PERSIST=true`

Flow:

1. app starts
2. fixture provider loads current state
3. simulator runs the default baseline simulation
4. history store checks whether `refreshed_at` already exists in history
5. if missing, it appends one entry and rewrites the history JSON file

Custom slider runs are never persisted.

## Deployment Architecture

The current production deployment path is:

```text
Local workspace
  -> Docker build
  -> ECR push
  -> AWS App Runner deployment
```

Deployment files:

- [Dockerfile](/Users/janardhanan/Desktop/learning/codex-drills/ipl/Dockerfile)
- [.dockerignore](/Users/janardhanan/Desktop/learning/codex-drills/ipl/.dockerignore)
- [deploy/apprunner-service.json](/Users/janardhanan/Desktop/learning/codex-drills/ipl/deploy/apprunner-service.json)

Runtime behavior in production:

- `gunicorn` serves `app:app`
- the container listens on `PORT`
- history persistence remains off by default

## Current Directory Structure

```text
ipl/
  app.py
  Dockerfile
  .dockerignore
  deploy/
    apprunner-service.json
  ipl_data/
    models.py
    fixture_provider.py
    history_store.py
    service.py
    state_store.py
    fixtures/
      ipl_2026_sample.json
      ipl_2026_qualification_history.json
  simulation/
    models.py
    engine.py
  templates/
    index.html
  static/
    css/
      styles.css
    js/
      app.js
    images/
      teams/
  tests/
    conftest.py
    test_api.py
    test_data_service.py
    test_history_store.py
    test_simulation_engine.py
```

## Error Handling Strategy

- malformed simulation counts return `400`
- simulation counts are clamped server-side
- missing history file falls back to empty history
- production avoids writing local history files

## Future Evolution

- add a live data refresh path later
- add more realistic NRR recomputation later if needed
- persist current state outside process memory later
- expand the history view and comparisons later
