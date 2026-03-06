from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/ai/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ai-service"


def test_cases_endpoint():
    response = client.get("/api/ai/cases")
    assert response.status_code == 200


def test_interrogation_endpoint():
    response = client.get("/api/ai/interrogation")
    assert response.status_code == 200


def test_mood_endpoint():
    response = client.get("/api/ai/mood")
    assert response.status_code == 200


def test_recommendations_endpoint():
    response = client.get("/api/ai/recommendations")
    assert response.status_code == 200
