import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.simulator import Scenario, simulate


def test_reproducible_and_conserved():
    scenario = Scenario()
    result = simulate(scenario)
    assert result == simulate(scenario)
    assert result["arrived"] == result["completed"] + result["backlog"]
    assert result["provenance"] == "synthetic_demo"
    assert all(0 <= zone["utilization"] <= 1 for zone in result["zones"])


def test_invalid_scenario():
    with pytest.raises(ValidationError):
        Scenario(pickers=0)


def test_api():
    client = TestClient(app)
    response = client.get("/api/v1/simulation/run?season=summer&seed=12")
    assert response.status_code == 200
    assert response.json()["scenario"]["season"] == "summer"
    assert client.get("/api/v1/simulation/run?pickers=0").status_code == 422
