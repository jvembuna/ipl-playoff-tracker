from __future__ import annotations

from app import create_app


def test_simulation_limit_is_enforced() -> None:
    app = create_app()
    app.config["TESTING"] = True
    app.config["MAX_SIMULATIONS"] = 25

    client = app.test_client()
    response = client.post(
        "/api/simulate",
        json={"simulation_count": 999999, "match_probabilities": {}},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["simulation_count"] == 25


def test_state_endpoint_returns_seeded_state() -> None:
    app = create_app()
    app.config["TESTING"] = True
    client = app.test_client()

    response = client.get("/api/state")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "ok"
    assert payload["state"]["standings"]
    assert "qualification_history" in payload["state"]
