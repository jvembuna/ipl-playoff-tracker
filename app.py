from __future__ import annotations

import os
from typing import Any

from flask import Flask, jsonify, render_template, request

from ipl_data.fixture_provider import FixtureStateProvider
from ipl_data.history_store import QualificationHistoryStore
from ipl_data.service import IPLDataService
from ipl_data.state_store import InMemoryStateStore
from simulation.engine import MonteCarloSimulator


def env_flag(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.lower() in {"1", "true", "yes", "on"}


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["APP_ENV"] = os.getenv("APP_ENV", "development")
    app.config["DEFAULT_SIMULATIONS"] = int(os.getenv("DEFAULT_SIMULATIONS", "10000"))
    app.config["MAX_SIMULATIONS"] = int(os.getenv("MAX_SIMULATIONS", "50000"))
    app.config["ENABLE_HISTORY_PERSIST"] = env_flag(
        "ENABLE_HISTORY_PERSIST",
        False,
    )

    state_store = InMemoryStateStore()
    fixture_provider = FixtureStateProvider()
    history_store = QualificationHistoryStore(fixture_provider=fixture_provider)
    simulator = MonteCarloSimulator()

    initial_state = fixture_provider.load_state()
    if app.config["ENABLE_HISTORY_PERSIST"] and app.config["APP_ENV"] == "development":
        baseline_result = simulator.run(
            standings=initial_state.standings,
            remaining_matches=initial_state.remaining_matches,
            match_probabilities={},
            simulation_count=app.config["DEFAULT_SIMULATIONS"],
        )
        initial_state = history_store.maybe_record_daily_snapshot(
            state=initial_state,
            qualification_percentages=baseline_result.qualification_percentages,
            simulation_count=app.config["DEFAULT_SIMULATIONS"],
        )
    state_store.set_state(initial_state)

    data_service = IPLDataService(state_store=state_store)
    app.extensions["data_service"] = data_service
    app.extensions["simulator"] = simulator

    @app.get("/")
    def index() -> str:
        return render_template(
            "index.html",
            default_simulations=app.config["DEFAULT_SIMULATIONS"],
            max_simulations=app.config["MAX_SIMULATIONS"],
        )

    @app.get("/api/state")
    def get_state() -> Any:
        state = data_service.get_state()
        return jsonify(
            {
                "status": "ok",
                "default_simulations": app.config["DEFAULT_SIMULATIONS"],
                "max_simulations": app.config["MAX_SIMULATIONS"],
                "state": state.to_dict(),
            }
        )

    @app.post("/api/simulate")
    def simulate() -> Any:
        payload = request.get_json(silent=True) or {}
        requested_simulations = payload.get(
            "simulation_count", app.config["DEFAULT_SIMULATIONS"]
        )
        try:
            requested_simulations = int(requested_simulations)
        except (TypeError, ValueError):
            return jsonify({"status": "error", "message": "simulation_count must be an integer"}), 400

        simulation_count = max(1, min(requested_simulations, app.config["MAX_SIMULATIONS"]))
        match_probabilities = payload.get("match_probabilities", {})

        state = data_service.get_state()
        result = simulator.run(
            standings=state.standings,
            remaining_matches=state.remaining_matches,
            match_probabilities=match_probabilities,
            simulation_count=simulation_count,
        )

        standings_by_team = {row.team_id: row for row in state.standings}
        ordered_standings = []
        for team_id, percentage in sorted(
            result.qualification_percentages.items(),
            key=lambda item: (
                item[1],
                standings_by_team[item[0]].points,
                item[0],
            ),
            reverse=True,
        ):
            row = standings_by_team[team_id]
            ordered_standings.append(
                {
                    **row.to_dict(),
                    "qualification_percentage": round(percentage, 1),
                }
            )

        return jsonify(
            {
                "status": "ok",
                "simulation_count": simulation_count,
                "qualification_percentages": {
                    team_id: round(value, 1)
                    for team_id, value in result.qualification_percentages.items()
                },
                "ordered_standings": ordered_standings,
                "match_probabilities": result.match_probabilities,
            }
        )

    return app


app = create_app()


if __name__ == "__main__":
    host = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
    port = int(os.getenv("PORT", os.getenv("FLASK_RUN_PORT", "5000")))
    debug = os.getenv("FLASK_DEBUG", "").lower() in {"1", "true", "yes", "on"}
    app.run(host=host, port=port, debug=debug)
