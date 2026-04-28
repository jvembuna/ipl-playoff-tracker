# Architecture

## Design Intent

This project should follow a small-module architecture with clear boundaries:

- Flask handles HTTP and template rendering
- `ipl_data` hides data retrieval and parsing details
- `simulation` owns qualification modeling and Monte Carlo logic
- the frontend renders state and sends simple API requests

The main rule is that simulation logic must not depend on Flask, and data-fetching details must not leak into the rest of the application.

This architecture also deliberately fixes the main structural limitations of the original notebook:

- avoid mutable global standings state during simulation
- avoid update-then-rollback recursion as the main engine
- avoid exhaustive binary branching when the number of matches grows

## Planned High-Level Flow

```text
Browser
  -> GET /
  -> Render HTML + CSS + JS

Browser action: Refresh IPL Data
  -> POST /api/refresh-data
  -> Flask route
  -> IPL data service
  -> refresh latest standings/results
  -> merge with stored season schedule
  -> in-memory app state update
  -> JSON response

Browser action: Run Simulation
  -> POST /api/simulate
  -> Flask route
  -> request validation
  -> simulation service
  -> qualification percentages
  -> JSON response
  -> frontend renders results
```

## Planned Module Boundaries

### Flask Layer

Responsibilities:

- define routes
- validate request payloads
- call service interfaces
- return JSON or HTML responses
- enforce server-side simulation limits

Should not contain:

- scraping logic
- Monte Carlo logic
- ranking logic

### `ipl_data` Layer

Responsibilities:

- ingest season schedule from the web or local fixture data
- refresh live IPL standings or completed results if possible
- normalize raw data into internal models
- load fallback JSON fixture data
- derive remaining matches from the stored schedule plus refreshed results
- expose a small refresh interface to the app

Suggested interface:

```python
state = data_service.refresh()
```

or

```python
state = provider.load_state()
```

### `simulation` Layer

Responsibilities:

- represent standings and matches
- derive per-match probabilities from user input
- run Monte Carlo trials
- rank teams and count qualification outcomes
- preserve the invariant that base input state is unchanged after a simulation request

Suggested interface:

```python
result = simulator.run(
    standings=...,
    remaining_matches=...,
    match_probabilities=...,
    simulation_count=...
)
```

Internally, each trial should operate on copied team state. That preserves the useful guarantee from the notebook that the original standings must not be altered by running a simulation, but does so without explicit rollback mechanics.

### Frontend Layer

Responsibilities:

- render current standings with qualification chance in the same table
- render remaining matches
- render one slider per remaining match, defaulted to 50/50
- call refresh and simulate endpoints
- display results and loading/error states

Should not contain:

- business rules for qualification
- sensitive trust in client-provided simulation limits

## Planned State Management

The application will store the current IPL state in memory on the server.

Implications:

- state is shared by all users
- state resets when the process restarts
- this is acceptable for V1

The state container should be wrapped in a small module so a future database-backed implementation can replace it with minimal changes.

## Planned Directory Structure

```text
ipl/
  app.py
  requirements.txt
  README.md
  SPEC.md
  ARCHITECTURE.md
  AGENTS.md
  TODO.md
  ipl_data/
    __init__.py
    models.py
    service.py
    state_store.py
    providers/
      __init__.py
      base.py
      results_provider.py
      schedule_provider.py
      fixture_provider.py
    fixtures/
      ipl_2026_sample.json
  simulation/
    __init__.py
    models.py
    probability.py
    engine.py
    qualification.py
  templates/
    index.html
  static/
    css/
      styles.css
    js/
      app.js
    images/
      logos/
  tests/
    test_data_service.py
    test_simulation_engine.py
    test_probability.py
    test_qualification.py
    test_api.py
```

## Data Flow

### Refresh Flow

1. User clicks refresh
2. Frontend calls `POST /api/refresh-data`
3. Flask route invokes the data service
4. Data service refreshes latest standings or completed results
5. The service merges refreshed results with the stored season schedule
6. Remaining matches are recalculated
7. Shared in-memory state is replaced
8. Response returns normalized state

### Simulation Flow

1. User adjusts sliders
2. Frontend sends simulation request
3. Flask validates and clamps simulation count
4. Simulation engine reads direct per-match win probabilities
5. Monte Carlo trials update copied standings, including placeholder NRR deltas
6. Qualification counts are aggregated
7. Percentages are returned to the UI

## Error Handling Strategy

- If live refresh fails, try fixture fallback if configured
- If both fail, return a clear JSON error
- If simulation input is malformed, return validation errors
- If no current state exists yet, simulation endpoint should fail clearly rather than guess

## Future Evolution

- add daily scheduled refresh at 11:30 AM PT
- persist refreshed state to disk or database
- support richer qualification rules
- support automatic schedule updates if needed
- add caching and observability
