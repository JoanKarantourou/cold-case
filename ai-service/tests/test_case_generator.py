"""Tests for AI case generation engine and endpoints."""

import asyncio
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db
from app.services.case_generator import CaseGenerator

# Mock database session
mock_db = MagicMock()


def override_get_db():
    yield mock_db


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# ── Unit Tests: CaseGenerator ──────────────────────


def test_resolve_params_defaults():
    gen = CaseGenerator()
    params = gen._resolve_params()
    assert "mood_tags" in params
    assert len(params["mood_tags"]) >= 2
    assert params["era"] in [
        "1950s", "1960s", "1970s", "1980s", "1990s", "2000s", "2010s"
    ]
    assert 1 <= params["difficulty"] <= 5
    assert params["crime_type"] is not None


def test_resolve_params_with_values():
    gen = CaseGenerator()
    params = gen._resolve_params(
        mood_tags=["dark", "foggy"],
        era="1970s",
        difficulty=3,
        crime_type="Murder",
    )
    assert params["mood_tags"] == ["dark", "foggy"]
    assert params["era"] == "1970s"
    assert params["difficulty"] == 3
    assert params["crime_type"] == "Murder"


def test_resolve_params_clamps_difficulty():
    gen = CaseGenerator()
    params = gen._resolve_params(difficulty=10)
    assert params["difficulty"] == 5
    params2 = gen._resolve_params(difficulty=0)
    assert params2["difficulty"] == 1


def test_generate_title():
    gen = CaseGenerator()
    titles = set()
    for _ in range(20):
        title = gen._generate_title()
        assert isinstance(title, str)
        assert len(title) > 3
        titles.add(title)
    # Should produce at least a few unique titles
    assert len(titles) > 3


def test_generate_case_number():
    gen = CaseGenerator()
    cn = gen._generate_case_number("1970s")
    assert cn.startswith("CASE #197")
    assert "-" in cn


def test_generate_setting():
    gen = CaseGenerator()
    setting = gen._generate_setting(["dark", "foggy"], "1970s")
    assert isinstance(setting, str)
    assert len(setting) > 20
    assert "1970s" in setting


def test_generate_victim():
    gen = CaseGenerator()
    victim = gen._generate_victim()
    assert "name" in victim
    assert "age" in victim
    assert "occupation" in victim
    assert "cause_of_death" in victim
    assert "background" in victim


def test_generate_suspects():
    gen = CaseGenerator()
    victim = {"name": "John Doe", "age": 50, "occupation": "Banker"}
    suspects = gen._generate_suspects(victim, 3, "Murder")
    assert len(suspects) == 3
    guilty_count = sum(1 for s in suspects if s["is_guilty"])
    assert guilty_count == 1
    for s in suspects:
        assert "name" in s
        assert "alibi" in s
        assert "hidden_knowledge" in s
        assert "personality_traits" in s


def test_generate_suspects_unique_names():
    gen = CaseGenerator()
    victim = {"name": "John Doe", "age": 50, "occupation": "Banker"}
    suspects = gen._generate_suspects(victim, 4, "Murder")
    names = [s["name"] for s in suspects]
    assert len(names) == len(set(names)), "Suspect names must be unique"
    assert "John Doe" not in names, "Suspect name must not match victim"


def test_generate_evidence():
    gen = CaseGenerator()
    suspects = [
        {"name": "A", "is_guilty": True},
        {"name": "B", "is_guilty": False},
        {"name": "C", "is_guilty": False},
    ]
    evidence = gen._generate_evidence(suspects, 8, 2)
    assert len(evidence) == 8
    red_herrings = [e for e in evidence if e["is_red_herring"]]
    assert len(red_herrings) == 2
    for ev in evidence:
        assert "type" in ev
        assert "title" in ev
        assert "description" in ev
        assert ev["type"] in ["PHYSICAL", "TESTIMONIAL", "FORENSIC", "DOCUMENTARY"]


def test_generate_case_files():
    gen = CaseGenerator()
    victim = {"name": "Jane Doe", "age": 35, "occupation": "Lawyer", "cause_of_death": "Blunt force trauma"}
    suspects = [{"name": "Tom", "is_guilty": True, "age": 40,
                 "occupation": "Mechanic", "relationship_to_victim": "Neighbor",
                 "alibi": "Was home", "hidden_knowledge": "Knows something"}]
    files = gen._generate_case_files(
        "Test Case", "CASE #1990-X", "1990s", "A dark alley",
        victim, suspects, 5,
    )
    assert len(files) == 5
    types = [f["type"] for f in files]
    assert "CRIME_SCENE_REPORT" in types
    for f in files:
        assert "title" in f
        assert "content" in f
        assert len(f["content"]) > 50


def test_parse_json_valid():
    gen = CaseGenerator()
    assert gen._parse_json('{"a": 1}') == {"a": 1}
    assert gen._parse_json('[1, 2]') == [1, 2]


def test_parse_json_with_markdown_fences():
    gen = CaseGenerator()
    result = gen._parse_json('```json\n{"key": "value"}\n```')
    assert result == {"key": "value"}


def test_parse_json_with_surrounding_text():
    gen = CaseGenerator()
    result = gen._parse_json('Here is the JSON: {"x": 1} done.')
    assert result == {"x": 1}


def test_parse_json_invalid():
    gen = CaseGenerator()
    assert gen._parse_json("not json at all") is None
    assert gen._parse_json(None) is None
    assert gen._parse_json("") is None


# ── Async generation test ────────────────────────


def test_generate_concept_fallback():
    """Test that concept generation works without LLM."""
    gen = CaseGenerator()
    gen._llm = None  # Force fallback
    params = gen._resolve_params(mood_tags=["dark", "foggy"], era="1970s", difficulty=3, crime_type="Murder")
    concept = asyncio.run(gen._generate_concept(params))
    assert "title" in concept
    assert "setting_description" in concept
    assert "synopsis" in concept
    assert "victim" in concept
    assert "name" in concept["victim"]


def test_generate_suspects_step_fallback():
    gen = CaseGenerator()
    gen._llm = None
    params = {"mood_tags": ["dark"], "era": "1970s", "difficulty": 3, "crime_type": "Murder"}
    concept = {
        "title": "Test",
        "synopsis": "A test case",
        "victim": {"name": "V", "age": 40, "occupation": "Banker", "background": ""},
    }
    suspects = asyncio.run(gen._generate_suspects_step(concept, params, 3))
    assert len(suspects) == 3
    assert sum(1 for s in suspects if s["is_guilty"]) == 1


def test_generate_evidence_step_fallback():
    gen = CaseGenerator()
    gen._llm = None
    params = {"mood_tags": ["dark"], "era": "1970s", "difficulty": 3, "crime_type": "Murder"}
    concept = {"title": "Test"}
    suspects = [
        {"name": "A", "is_guilty": True},
        {"name": "B", "is_guilty": False},
    ]
    evidence = asyncio.run(gen._generate_evidence_step(concept, suspects, params, 8, 2))
    assert len(evidence) == 8


# ── Endpoint Tests ───────────────────────────────


def test_generate_endpoint():
    """Test that the generate endpoint returns a generation_id."""
    # Mock the DB operations
    mock_gen = MagicMock()
    mock_gen.id = 42
    mock_gen.status = "PROCESSING"
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock(side_effect=lambda obj: setattr(obj, "id", 42))

    with patch("app.routers.cases.run_generation_in_background") as mock_bg:
        mock_bg.return_value = None
        response = client.post(
            "/api/ai/cases/generate",
            json={"mood_tags": ["dark"], "era": "1970s"},
        )

    assert response.status_code == 200
    data = response.json()
    assert "generation_id" in data
    assert data["status"] == "PROCESSING"


def test_generation_status_not_found():
    """Test 404 for unknown generation ID — uses fresh DB override."""
    fresh_mock = MagicMock()
    fresh_mock.query.return_value.filter.return_value.first.return_value = None
    app.dependency_overrides[get_db] = lambda: (yield fresh_mock).__next__() or fresh_mock

    def _override():
        yield fresh_mock

    app.dependency_overrides[get_db] = _override
    test_client = TestClient(app)
    response = test_client.get("/api/ai/cases/generate/99999")
    assert response.status_code == 404
    app.dependency_overrides[get_db] = override_get_db


def test_generation_status_complete():
    """Test completed generation returns case summary."""
    fresh_mock = MagicMock()

    mock_req = MagicMock()
    mock_req.id = 1
    mock_req.status = "COMPLETE"
    mock_req.case_id = 10
    mock_req.created_at = MagicMock(isoformat=lambda: "2026-01-01T00:00:00")
    mock_req.completed_at = MagicMock(isoformat=lambda: "2026-01-01T00:01:00")

    mock_case = MagicMock()
    mock_case.id = 10
    mock_case.title = "Generated Case"
    mock_case.case_number = "CASE #1990-X"
    mock_case.classification = "COLD"
    mock_case.difficulty = 3
    mock_case.mood_tags = ["dark"]
    mock_case.era = "1990s"
    mock_case.synopsis = "A test."

    # First query call: generation request, second: case lookup
    gen_query = MagicMock()
    gen_query.filter.return_value.first.return_value = mock_req
    case_query = MagicMock()
    case_query.filter.return_value.first.return_value = mock_case
    fresh_mock.query.side_effect = [gen_query, case_query]

    def _override():
        yield fresh_mock

    app.dependency_overrides[get_db] = _override
    test_client = TestClient(app)
    response = test_client.get("/api/ai/cases/generate/1")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETE"
    app.dependency_overrides[get_db] = override_get_db
