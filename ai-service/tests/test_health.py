import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db

# Mock database session for tests
mock_db = MagicMock()


def override_get_db():
    yield mock_db


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/ai/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ai-service"


def test_cases_endpoint():
    mock_db.query.return_value.all.return_value = []
    mock_db.query.return_value.filter.return_value.all.return_value = []
    response = client.get("/api/ai/cases")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_case_not_found():
    mock_db.query.return_value.filter.return_value.first.return_value = None
    response = client.get("/api/ai/cases/9999")
    assert response.status_code == 404


def test_interrogation_endpoint():
    response = client.get("/api/ai/interrogation")
    assert response.status_code == 200


def test_mood_endpoint():
    response = client.get("/api/ai/mood")
    assert response.status_code == 200


def test_recommendations_endpoint():
    response = client.get("/api/ai/recommendations")
    assert response.status_code == 200
