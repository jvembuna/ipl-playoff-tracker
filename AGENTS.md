# Agent Guide

## Purpose

This file explains how humans and coding agents should work on this repository safely and consistently.

## Current Project Phase

The repository is currently in Phase 0 planning unless the user explicitly approves implementation.

Until approval:

- create and refine documentation
- improve plans
- clarify assumptions
- do not add application code

## Working Principles

- Keep modules small and interfaces deep
- Prefer simple public APIs over clever internal coupling
- Keep Flask concerns out of simulation logic
- Keep data-source concerns out of the rest of the app
- Preserve clean fallback behavior from live data to fixture data
- Make deterministic choices where ambiguity would hurt testing
- Preserve useful notebook invariants while removing notebook-era structural shortcuts

## Safe Boundaries

### Do

- update documentation when design changes
- keep simulation logic framework-independent
- add tests for each behavior boundary
- prefer explicit models over loose dictionaries when reasonable
- isolate tie-break rules in one module
- isolate probability translation in one module
- keep base standings unchanged after simulation

### Do Not

- spread IPL ranking logic across routes, templates, and scripts
- hard-code brittle scraping assumptions directly inside Flask routes
- let the frontend choose unsafe simulation counts without server enforcement
- introduce a database in the first version unless explicitly approved
- mix fallback fixture parsing with simulation code
- reintroduce global-mutation-plus-rollback as the main simulation pattern

## Planned Interfaces To Preserve

### Data Refresh Interface

The rest of the app should interact with data loading through a small service boundary, not through provider-specific code.

Treat schedule ingestion and standings refresh as separate concerns:

- schedule data can be captured once and stored locally
- daily-changing standings/results data is what manual refresh updates

### Simulation Interface

The rest of the app should call one simulation entry point that accepts:

- standings
- remaining matches
- direct per-match probability settings
- simulation count

and returns:

- qualification percentages
- metadata if helpful

## Change Strategy

When implementing:

1. start with domain models
2. build the fixture-backed data path first
3. add live data integration behind the same interface
4. add simulation engine with unit tests
5. connect Flask routes last
6. keep frontend JavaScript thin

Migration notes from the 2024 notebook:

- keep qualification defined as finishing in the top 4
- keep primary ranking as points then NRR
- replace exhaustive recursion with Monte Carlo sampling
- keep the placeholder NRR adjustment policy isolated in one place
- move from team-level assumptions to explicit per-match slider inputs in the UI

## Testing Expectations

At minimum, maintain tests for:

- standings normalization
- remaining-match derivation from stored schedule and refreshed results
- probability validation and clamping
- simulation outcomes
- qualification counting
- tie-break behavior
- API guardrails such as simulation count clamping

## Handoff Notes For Future Agents

- Read [README.md](/Users/janardhanan/Desktop/learning/codex-drills/ipl/README.md), [SPEC.md](/Users/janardhanan/Desktop/learning/codex-drills/ipl/SPEC.md), and [ARCHITECTURE.md](/Users/janardhanan/Desktop/learning/codex-drills/ipl/ARCHITECTURE.md) before implementation
- Confirm the current phase before writing code
- If live data fetching is brittle, keep the fixture-backed path working and make that the default development route
- If qualification rules become more detailed later, extend `simulation/qualification.py` rather than scattering rule logic
