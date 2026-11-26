from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_liveness():
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_metrics_have_provenance():
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    metrics = response.json()
    assert len(metrics) == 4
    assert all(m["provenance"] == "synthetic_demo" for m in metrics)
