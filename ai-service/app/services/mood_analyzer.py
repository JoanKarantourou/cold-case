"""
Mood Analyzer — Image and text mood analysis for case matching.

Uses HuggingFace Inference API with BLIP model for image captioning,
then maps extracted features to mood tags for case recommendations.
Falls back to keyword-based analysis when no API token is configured.
"""

import base64
import io
import logging
from typing import Optional

import httpx
from PIL import Image

from app.config import settings
from app.models.db_models import CaseDB

logger = logging.getLogger(__name__)

VALID_MOODS = [
    "dark", "foggy", "melancholic", "neon", "sterile", "paranoid",
    "eerie", "nostalgic", "warm", "cold", "urban", "rural",
    "industrial", "coastal", "small-town",
]

SETTING_TYPES = ["indoor", "outdoor", "urban", "rural", "modern", "vintage"]
TIME_OF_DAY = ["dawn", "morning", "afternoon", "evening", "night"]

# Keyword-to-mood mappings for text and caption analysis
KEYWORD_MOOD_MAP: dict[str, list[str]] = {
    # Nature / landscape
    "fog": ["foggy", "eerie", "melancholic"],
    "mist": ["foggy", "eerie"],
    "lake": ["melancholic", "dark", "cold"],
    "water": ["melancholic", "cold", "coastal"],
    "ocean": ["coastal", "cold", "melancholic"],
    "sea": ["coastal", "cold"],
    "beach": ["coastal", "warm"],
    "forest": ["dark", "eerie", "rural"],
    "tree": ["rural", "nostalgic"],
    "mountain": ["cold", "rural"],
    "field": ["rural", "nostalgic"],
    "farm": ["rural", "nostalgic", "small-town"],
    "rain": ["dark", "melancholic", "cold"],
    "storm": ["dark", "eerie"],
    "snow": ["cold", "melancholic"],
    "sunset": ["warm", "melancholic", "nostalgic"],
    "sunrise": ["warm"],
    "night": ["dark", "eerie"],
    "dark": ["dark", "eerie"],
    "shadow": ["dark", "eerie"],
    "moon": ["dark", "eerie", "nostalgic"],

    # Urban / architecture
    "city": ["urban", "neon", "industrial"],
    "building": ["urban", "industrial"],
    "skyscraper": ["urban", "neon", "sterile"],
    "street": ["urban", "dark"],
    "alley": ["urban", "dark", "paranoid"],
    "neon": ["neon", "urban", "paranoid"],
    "sign": ["neon", "urban"],
    "factory": ["industrial", "sterile"],
    "warehouse": ["industrial", "dark"],
    "bridge": ["urban", "melancholic"],
    "church": ["nostalgic", "eerie", "small-town"],
    "house": ["nostalgic", "small-town"],
    "cabin": ["rural", "eerie", "dark"],
    "hospital": ["sterile", "paranoid"],
    "office": ["sterile", "urban"],
    "laboratory": ["sterile", "paranoid"],
    "computer": ["sterile", "neon", "paranoid"],
    "screen": ["neon", "sterile", "paranoid"],

    # Atmosphere / emotion
    "abandoned": ["eerie", "dark", "industrial"],
    "lonely": ["melancholic", "dark"],
    "empty": ["eerie", "sterile", "melancholic"],
    "old": ["nostalgic", "eerie"],
    "vintage": ["nostalgic"],
    "retro": ["nostalgic", "neon"],
    "quiet": ["eerie", "melancholic", "small-town"],
    "silent": ["eerie", "dark"],
    "mysterious": ["dark", "eerie", "paranoid"],
    "gloomy": ["dark", "melancholic", "foggy"],
    "warm": ["warm", "nostalgic"],
    "cold": ["cold", "dark"],
    "isolated": ["eerie", "rural", "melancholic"],
    "desolate": ["dark", "eerie", "cold"],
    "rustic": ["rural", "nostalgic", "small-town"],
    "town": ["small-town", "nostalgic"],
    "village": ["small-town", "rural"],
    "radio": ["nostalgic", "eerie"],
}

# Color palette keyword mappings
COLOR_MOOD_MAP: dict[str, list[str]] = {
    "green": ["foggy", "rural", "eerie"],
    "blue": ["cold", "melancholic", "coastal"],
    "red": ["dark", "warm", "paranoid"],
    "orange": ["warm", "nostalgic"],
    "yellow": ["warm", "neon"],
    "purple": ["dark", "neon", "eerie"],
    "black": ["dark", "eerie"],
    "white": ["sterile", "cold"],
    "gray": ["foggy", "melancholic", "industrial"],
    "grey": ["foggy", "melancholic", "industrial"],
    "brown": ["nostalgic", "rural", "warm"],
}


class MoodAnalysisResult:
    """Result of mood analysis from image or text."""

    def __init__(
        self,
        dominant_moods: list[str],
        color_palette: list[str],
        setting_type: list[str],
        time_of_day: str,
        atmospheric_keywords: list[str],
        caption: str = "",
    ):
        self.dominant_moods = dominant_moods
        self.color_palette = color_palette
        self.setting_type = setting_type
        self.time_of_day = time_of_day
        self.atmospheric_keywords = atmospheric_keywords
        self.caption = caption

    def to_dict(self) -> dict:
        return {
            "dominant_moods": self.dominant_moods,
            "color_palette": self.color_palette,
            "setting_type": self.setting_type,
            "time_of_day": self.time_of_day,
            "atmospheric_keywords": self.atmospheric_keywords,
            "caption": self.caption,
        }


class MoodAnalyzer:
    """Analyzes images and text to extract mood tags for case matching."""

    HF_BLIP_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"

    def __init__(self):
        self.api_token = settings.huggingface_api_token

    async def analyze_image(self, image_data: bytes) -> MoodAnalysisResult:
        """Analyze an image and extract mood information."""
        caption = await self._get_image_caption(image_data)
        logger.info(f"Image caption: {caption}")
        return self._analyze_text(caption)

    async def analyze_text(self, description: str) -> MoodAnalysisResult:
        """Analyze a text description and extract mood information."""
        return self._analyze_text(description)

    async def _get_image_caption(self, image_data: bytes) -> str:
        """Get a text caption for an image using HuggingFace BLIP model."""
        if not self.api_token:
            logger.warning("No HuggingFace API token — using fallback caption")
            return self._fallback_image_analysis(image_data)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.HF_BLIP_URL,
                    headers={"Authorization": f"Bearer {self.api_token}"},
                    content=image_data,
                )
                response.raise_for_status()
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "")
                return str(result)
        except Exception as e:
            logger.warning(f"HuggingFace API call failed: {e} — using fallback")
            return self._fallback_image_analysis(image_data)

    def _fallback_image_analysis(self, image_data: bytes) -> str:
        """Basic image analysis using PIL when HuggingFace API is unavailable."""
        try:
            img = Image.open(io.BytesIO(image_data))
            img_small = img.resize((100, 100)).convert("RGB")
            pixels = list(img_small.get_flattened_data())

            avg_r = sum(p[0] for p in pixels) / len(pixels)
            avg_g = sum(p[1] for p in pixels) / len(pixels)
            avg_b = sum(p[2] for p in pixels) / len(pixels)

            brightness = (avg_r + avg_g + avg_b) / 3

            descriptors = []
            if brightness < 80:
                descriptors.extend(["dark", "night", "shadow", "gloomy"])
            elif brightness < 140:
                descriptors.extend(["dim", "evening", "moody"])
            else:
                descriptors.extend(["bright", "daylight"])

            if avg_b > avg_r and avg_b > avg_g:
                descriptors.extend(["blue", "cold", "water"])
            elif avg_g > avg_r and avg_g > avg_b:
                descriptors.extend(["green", "forest", "nature"])
            elif avg_r > avg_g and avg_r > avg_b:
                descriptors.extend(["red", "warm"])

            if avg_r > 180 and avg_g > 160 and avg_b < 100:
                descriptors.append("sunset")
            if avg_r < 60 and avg_g < 60 and avg_b < 60:
                descriptors.append("night")

            w, h = img.size
            if w > h * 1.5:
                descriptors.append("landscape")
            if h > w:
                descriptors.append("portrait")

            return " ".join(descriptors)
        except Exception as e:
            logger.warning(f"Fallback image analysis failed: {e}")
            return "mysterious dark scene"

    def _analyze_text(self, text: str) -> MoodAnalysisResult:
        """Extract mood features from text (caption or user description)."""
        text_lower = text.lower()
        words = text_lower.split()

        mood_scores: dict[str, float] = {m: 0.0 for m in VALID_MOODS}
        detected_keywords: list[str] = []
        detected_colors: list[str] = []
        detected_settings: list[str] = []

        # Score moods from keyword matches
        for keyword, moods in KEYWORD_MOOD_MAP.items():
            if keyword in text_lower:
                detected_keywords.append(keyword)
                for mood in moods:
                    mood_scores[mood] += 1.0

        # Score moods from color matches
        for color, moods in COLOR_MOOD_MAP.items():
            if color in text_lower:
                detected_colors.append(color)
                for mood in moods:
                    mood_scores[mood] += 0.5

        # Detect setting type
        indoor_keywords = {"room", "house", "building", "office", "hospital", "laboratory", "kitchen", "bedroom", "indoor"}
        outdoor_keywords = {"field", "forest", "lake", "ocean", "mountain", "street", "garden", "outdoor", "sky"}
        urban_keywords = {"city", "building", "skyscraper", "street", "alley", "neon", "urban"}
        rural_keywords = {"farm", "field", "forest", "village", "cabin", "rural", "countryside"}
        modern_keywords = {"computer", "screen", "neon", "skyscraper", "modern", "digital"}
        vintage_keywords = {"old", "vintage", "retro", "antique", "classic", "rustic"}

        for kw_set, label in [
            (indoor_keywords, "indoor"), (outdoor_keywords, "outdoor"),
            (urban_keywords, "urban"), (rural_keywords, "rural"),
            (modern_keywords, "modern"), (vintage_keywords, "vintage"),
        ]:
            if any(kw in words for kw in kw_set):
                detected_settings.append(label)

        if not detected_settings:
            detected_settings = ["outdoor"] if mood_scores.get("rural", 0) > mood_scores.get("urban", 0) else ["urban"]

        # Detect time of day
        time = "evening"  # default
        for kw, t in [
            ("dawn", "dawn"), ("sunrise", "dawn"), ("morning", "morning"),
            ("afternoon", "afternoon"), ("noon", "afternoon"),
            ("sunset", "evening"), ("evening", "evening"), ("dusk", "evening"),
            ("night", "night"), ("midnight", "night"), ("dark", "night"),
        ]:
            if kw in text_lower:
                time = t
                break

        # Get top moods sorted by score
        sorted_moods = sorted(mood_scores.items(), key=lambda x: x[1], reverse=True)
        dominant_moods = [m for m, s in sorted_moods if s > 0][:5]

        if not dominant_moods:
            dominant_moods = ["dark", "melancholic"]

        if not detected_colors:
            detected_colors = self._infer_colors_from_moods(dominant_moods)

        return MoodAnalysisResult(
            dominant_moods=dominant_moods,
            color_palette=detected_colors or ["gray"],
            setting_type=detected_settings,
            time_of_day=time,
            atmospheric_keywords=detected_keywords[:8],
            caption=text,
        )

    def _infer_colors_from_moods(self, moods: list[str]) -> list[str]:
        """Infer likely color palette from mood tags."""
        mood_color = {
            "dark": "black", "foggy": "gray", "melancholic": "blue",
            "neon": "purple", "sterile": "white", "paranoid": "red",
            "eerie": "gray", "nostalgic": "brown", "warm": "orange",
            "cold": "blue", "urban": "gray", "rural": "green",
            "industrial": "gray", "coastal": "blue", "small-town": "brown",
        }
        return list(dict.fromkeys(mood_color.get(m, "gray") for m in moods))[:4]

    @staticmethod
    def match_cases(
        analysis: MoodAnalysisResult,
        cases: list[CaseDB],
    ) -> list[dict]:
        """Match mood analysis against cases and return ranked recommendations."""
        results = []
        query_moods = set(analysis.dominant_moods)

        for case in cases:
            case_moods = set(case.mood_tags)
            if not case_moods:
                continue

            intersection = query_moods & case_moods
            union = query_moods | case_moods
            jaccard = len(intersection) / len(union) if union else 0

            overlap_ratio = len(intersection) / len(query_moods) if query_moods else 0

            match_pct = round((jaccard * 0.4 + overlap_ratio * 0.6) * 100)
            match_pct = min(match_pct, 99)

            if match_pct > 0:
                results.append({
                    "case_id": case.id,
                    "title": case.title,
                    "case_number": case.case_number,
                    "classification": case.classification,
                    "difficulty": case.difficulty,
                    "mood_tags": case.mood_tags,
                    "era": case.era,
                    "synopsis": case.synopsis,
                    "mood_match_percentage": match_pct,
                    "matched_moods": list(intersection),
                })

        results.sort(key=lambda x: x["mood_match_percentage"], reverse=True)
        return results


mood_analyzer = MoodAnalyzer()
