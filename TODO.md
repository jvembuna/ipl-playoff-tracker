# TODO

## Phase 0: Planning

- [x] Create repository planning documents
- [x] Define project scope and non-goals
- [x] Define initial API shape
- [x] Define architecture and module boundaries
- [x] Define safe agent workflow guidance
- [x] Capture lessons from the 2024 notebook
- [x] Stop and wait for implementation approval

## Phase 1: Foundation

- [ ] Create Python project skeleton
- [ ] Add Flask and test dependencies
- [ ] Add application entry point
- [ ] Add basic template and static asset structure

## Phase 2: IPL Data

- [ ] Define internal standings and match models
- [ ] Implement fixture JSON loader
- [ ] Add normalized season schedule fixture data
- [ ] Investigate practical live standings and fixture source
- [ ] Implement one-time schedule ingestion path
- [ ] Implement daily results or standings refresh provider
- [ ] Implement refresh service with fallback behavior
- [ ] Derive remaining matches from schedule minus completed matches
- [ ] Add tests for data normalization and fallback handling

## Phase 3: Simulation

- [ ] Implement per-match probability validation
- [ ] Implement Monte Carlo simulation engine
- [ ] Implement qualification counting
- [ ] Implement isolated tie-break logic
- [ ] Implement fixed simulated NRR delta policy of `+0.1/-0.1`
- [ ] Add tests for probability handling
- [ ] Add tests for qualification counting
- [ ] Add tests for tie-break behavior

## Phase 4: Web App

- [ ] Implement `GET /`
- [ ] Implement `POST /api/refresh-data`
- [ ] Implement `GET /api/state`
- [ ] Implement `POST /api/simulate`
- [ ] Add server-side simulation limit enforcement
- [ ] Build standings table with qualification chance included
- [ ] Sort standings display by qualification chance after simulation
- [ ] Add one 50/50 slider for each remaining match
- [ ] Add loading and error states

## Phase 5: Polish

- [ ] Add simple styling
- [ ] Add optional team logos if practical
- [ ] Improve copy and empty states
- [ ] Verify local run instructions
- [ ] Verify tests pass end to end

## Open Questions

- Which live source is stable enough for standings and fixtures in practice?
- Should missing net run rate values default to zero or trigger a different deterministic ranking fallback?
