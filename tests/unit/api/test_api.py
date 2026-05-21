"""API tests for the HTTP boundary."""

from fastapi.testclient import TestClient

from tarot_engine.api.app import app
from tests.unit.application.test_services import _build_move_fixture

client = TestClient(app)


def test_health_endpoint_returns_ok() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["api_version"] == "v1"



def test_meta_contracts_endpoint_returns_available_contracts() -> None:
    response = client.get("/api/v1/meta/contracts")
    assert response.status_code == 200
    assert response.json() == ["PRISE", "GARDE", "GARDE_SANS", "GARDE_CONTRE"]



def test_move_recommendation_endpoint_returns_structured_payload() -> None:
    remaining_hand, completed_tricks, current_trick = _build_move_fixture()
    response = client.post(
        "/api/v1/moves/recommend",
        json={
            "remaining_hand": remaining_hand,
            "contract": "GARDE",
            "player_index": 0,
            "taker_index": 0,
            "partner_index": None,
            "completed_tricks": list(completed_tricks),
            "current_trick": current_trick,
            "next_player_index": 0,
            "n_samples": 8,
            "seed": 7,
            "policy": "expected_score",
        },
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["recommended_action"]["player_index"] == 0
    assert payload["policy_name"] == "expected_score"
    assert len(payload["ranked_actions"]) >= 1
    assert payload["explanation"]["summary"]
