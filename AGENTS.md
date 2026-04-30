# Agent Guide

## Purpose

This file explains how humans and coding agents should work on this repository safely and consistently.

## Current Repository State

This is no longer a planning-only repository. The app is implemented, tested, containerized, and deployed.

Current shape:

- fixture-backed Flask app
- Monte Carlo simulation engine
- qualification history chart
- AWS App Runner deployment path

## Working Principles

- keep modules small and interfaces simple
- prefer clarity over defensive abstraction
- keep Flask concerns out of the simulator
- keep fixture and history file logic out of route handlers
- do not add speculative complexity without a clear need
- preserve the current manual-data workflow unless the user asks to automate it

## Safe Boundaries

### Do

- update documentation when behavior changes
- keep simulation logic framework-independent
- add tests around behavior boundaries
- keep current JSON fixtures readable and one-line-per-entity
- preserve baseline-history-only persistence behavior
- keep production file writes disabled unless explicitly redesigned

### Do Not

- reintroduce unfinished live-refresh code paths casually
- spread ranking logic across routes, templates, and scripts
- let the frontend control unsafe simulation counts
- add a database unless explicitly requested
- silently change the manual fixture update workflow
- persist custom slider runs into history

## Interfaces To Preserve

### State Loading

The rest of the app should continue to interact with current IPL data through the fixture provider and data service rather than reading JSON files directly from route handlers.

### Simulation

The rest of the app should call one simulation entry point that accepts:

- standings
- remaining matches
- direct per-match probability settings
- simulation count

and returns:

- qualification percentages
- normalized match probabilities

### History Persistence

History persistence currently means:

- baseline 50/50 run only
- one entry per `refreshed_at` date
- development-only opt-in

Keep that contract stable unless the user asks to change it.

## Change Strategy

When extending the app:

1. update the domain model first if needed
2. keep fixture-backed behavior working
3. add tests for the new behavior boundary
4. wire Flask routes after core logic is settled
5. keep frontend JavaScript thin

## Testing Expectations

Maintain coverage for:

- state loading
- simulation behavior
- history persistence rules
- API guardrails such as simulation count clamping

Run:

```bash
pytest
```

## Deployment Notes

Current deployment target:

- AWS App Runner

Current deployment path:

1. build Docker image
2. push to ECR
3. start App Runner deployment

Key files:

- [Dockerfile](/Users/janardhanan/Desktop/learning/codex-drills/ipl/Dockerfile)
- [deploy/apprunner-service.json](/Users/janardhanan/Desktop/learning/codex-drills/ipl/deploy/apprunner-service.json)

## Handoff Notes For Future Agents

- Read [README.md](/Users/janardhanan/Desktop/learning/codex-drills/ipl/README.md), [SPEC.md](/Users/janardhanan/Desktop/learning/codex-drills/ipl/SPEC.md), and [ARCHITECTURE.md](/Users/janardhanan/Desktop/learning/codex-drills/ipl/ARCHITECTURE.md) before making changes
- Treat the fixture files as an intentional manual workflow, not a temporary mistake
- Keep the history file separate from the main snapshot file
- If live data fetching returns later, add it behind a clean boundary rather than reviving stale planned code
