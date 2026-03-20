"""Tests for mood analysis endpoints and service."""

import io
import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app
from app.database import get_db
from app.services.mood_analyzer import MoodAnalyzer, MoodAnalysisResult

# Mock database session for tests
mock_db = MagicMock()


def override_get_db():
    yield mock_db


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# ─── Service Tests ───


def test_analyze_text_dark_foggy():
    analyzer = MoodAnalyzer()
    import asyncio
    result = asyncio.run(
        analyzer.analyze_text("dark foggy lake at night")
    )
    assert "dark" in result.dominant_moods
    assert "foggy" in result.dominant_moods
    assert result.time_of_day == "night"


def test_analyze_text_urban_neon():
    analyzer = MoodAnalyzer()
    import asyncio
    result = asyncio.run(
        analyzer.analyze_text("neon city street with skyscrapers")
    )
    assert "neon" in result.dominant_moods
    assert "urban" in result.dominant_moods
    assert "urban" in result.setting_type


def test_analyze_text_nostalgic_rural():
    analyzer = MoodAnalyzer()
    import asyncio
    result = asyncio.run(
        analyzer.analyze_text("old rustic farm village with vintage radio")
    )
    assert "nostalgic" in result.dominant_moods
    assert "rural" in result.dominant_moods or "small-town" in result.dominant_moods


def test_analyze_text_empty_returns_defaults():
    analyzer = MoodAnalyzer()
    import asyncio
    result = asyncio.run(
        analyzer.analyze_text("xyz zzz qqq")
    )
    assert len(result.dominant_moods) > 0
    assert isinstance(result.color_palette, list)


def test_mood_analysis_result_to_dict():
    result = MoodAnalysisResult(
        dominant_moods=["dark", "foggy"],
        color_palette=["gray", "blue"],
        setting_type=["outdoor"],
        time_of_day="night",
        atmospheric_keywords=["fog", "lake"],
        caption="test caption",
    )
    d = result.to_dict()
    assert d["dominant_moods"] == ["dark", "foggy"]
    assert d["caption"] == "test caption"


def test_match_cases_ranking():
    """Cases with more mood overlap should rank higher."""
    analyzer = MoodAnalyzer()
    analysis = MoodAnalysisResult(
        dominant_moods=["dark", "foggy", "melancholic"],
        color_palette=["gray"],
        setting_type=["outdoor"],
        time_of_day="night",
        atmospheric_keywords=[],
    )

    case_a = MagicMock()
    case_a.id = 1
    case_a.title = "Lake House"
    case_a.case_number = "CASE #1977-B"
    case_a.classification = "COLD"
    case_a.difficulty = 3
    case_a.mood_tags = ["dark", "foggy", "melancholic"]
    case_a.era = "1970s"
    case_a.synopsis = "A body in the lake."

    case_b = MagicMock()
    case_b.id = 2
    case_b.title = "Digital Ghost"
    case_b.case_number = "CASE #2003-K"
    case_b.classification = "COLD"
    case_b.difficulty = 4
    case_b.mood_tags = ["sterile", "neon", "paranoid"]
    case_b.era = "2000s"
    case_b.synopsis = "A programmer vanishes."

    results = MoodAnalyzer.match_cases(analysis, [case_a, case_b])
    assert len(results) >= 1
    assert results[0]["case_id"] == 1
    assert results[0]["mood_match_percentage"] > 0


def test_match_cases_no_cases():
    analysis = MoodAnalysisResult(
        dominant_moods=["dark"],
        color_palette=[],
        setting_type=[],
        time_of_day="night",
        atmospheric_keywords=[],
    )
    results = MoodAnalyzer.match_cases(analysis, [])
    assert results == []


# ─── Endpoint Tests ───


def test_mood_status():
    response = client.get("/api/ai/mood")
    assert response.status_code == 200


def test_analyze_text_endpoint():
    mock_db.query.return_value.all.return_value = []
    response = client.post(
        "/api/ai/mood/analyze-text",
        json={"description": "dark foggy night near a lake"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "dominant_moods" in data
    assert "recommendations" in data
    assert "dark" in data["dominant_moods"]


def test_analyze_text_endpoint_empty():
    response = client.post(
        "/api/ai/mood/analyze-text",
        json={"description": ""},
    )
    # Empty string still gets processed (returns defaults)
    assert response.status_code == 200


def test_analyze_image_endpoint():
    """Test image upload with a small generated test image."""
    mock_db.query.return_value.all.return_value = []

    img = Image.new("RGB", (50, 50), color=(20, 30, 60))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    response = client.post(
        "/api/ai/mood/analyze",
        files={"image": ("test.png", buf, "image/png")},
    )
    assert response.status_code == 200
    data = response.json()
    assert "dominant_moods" in data
    assert "recommendations" in data


def test_analyze_no_input():
    response = client.post("/api/ai/mood/analyze")
    assert response.status_code == 400


def test_analyze_non_image_file():
    response = client.post(
        "/api/ai/mood/analyze",
        files={"image": ("test.txt", b"not an image", "text/plain")},
    )
    assert response.status_code == 400


def test_fallback_image_analysis():
    """Test the PIL fallback when no HF token is set."""
    analyzer = MoodAnalyzer()
    # Dark image
    img = Image.new("RGB", (50, 50), color=(10, 10, 10))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    caption = analyzer._fallback_image_analysis(buf.getvalue())
    assert "dark" in caption or "night" in caption

    # Blue image
    img_blue = Image.new("RGB", (50, 50), color=(30, 50, 200))
    buf2 = io.BytesIO()
    img_blue.save(buf2, format="PNG")
    caption2 = analyzer._fallback_image_analysis(buf2.getvalue())
    assert "blue" in caption2 or "cold" in caption2
