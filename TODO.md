# TODO

## Current Baseline

- [x] Build the Flask web app
- [x] Add fixture-backed standings and remaining matches
- [x] Add Monte Carlo simulation
- [x] Add server-side simulation clamping
- [x] Add standings table with qualification chance
- [x] Add per-match probability sliders
- [x] Add qualification history chart
- [x] Add team logos
- [x] Add Docker and AWS App Runner deployment path

## Next Product Improvements

- [ ] Improve chart readability as daily history grows
- [ ] Consider richer hover or comparison behavior in the history chart
- [ ] Decide whether to add a lightweight way to surface the current seed date in the UI
- [ ] Consider a simple "reset all sliders to 50/50" action
- [ ] Consider showing the currently selected highlighted team more explicitly in the chart legend

## Data Workflow

- [ ] Decide whether to keep manual JSON updates indefinitely or reintroduce a live refresh path later
- [ ] If live refresh returns, keep the current manual fixture path as a safe fallback
- [ ] Consider adding a small validation script for manual standings and match edits

## Simulation Improvements

- [ ] Decide whether the points-only tie-break is good enough or should be refined
- [ ] Consider future no-result simulation only if there is a clear product need
- [ ] Consider exposing a small set of preset simulation counts in the UI

## Deployment Improvements

- [ ] Decide whether to vendor Chart.js locally instead of using a CDN
- [ ] Add a short deployment runbook to the repo if AWS deploys become a regular workflow
- [ ] Consider pushing committed code only for production deploys as a stricter workflow

## Open Questions

- When history gets denser, should the default chart view show all teams or start in a more focused mode?
- Should future history snapshots continue to be keyed by `refreshed_at`, or should that ever diverge from the manually maintained seed date?
