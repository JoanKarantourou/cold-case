"""Mood analysis router — image upload and text-based mood matching."""

import base64
import logging
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import CaseDB
from app.services.mood_analyzer import mood_analyzer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai/mood", tags=["mood"])

MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB


class TextMoodRequest(BaseModel):
    description: str


class MoodAnalysisResponse(BaseModel):
    dominant_moods: list[str]
    color_palette: list[str]
    setting_type: list[str]
    time_of_day: str
    atmospheric_keywords: list[str]
    caption: str
    recommendations: list[dict]


@router.get("")
async def mood_status():
    return {"message": "Mood analysis endpoint — upload an image or describe a mood"}


@router.post("/analyze", response_model=MoodAnalysisResponse)
async def analyze_mood(
    image: Optional[UploadFile] = File(None),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """Analyze an uploaded image or text description and return mood-matched cases."""
    if image is None and not description:
        raise HTTPException(
            status_code=400,
            detail="Provide either an image upload or a text description",
        )

    if image is not None:
        content_type = image.content_type or ""
        if not content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        image_data = await image.read()
        if len(image_data) > MAX_IMAGE_SIZE:
            raise HTTPException(status_code=400, detail="Image exceeds 10 MB limit")

        analysis = await mood_analyzer.analyze_image(image_data)
    else:
        analysis = await mood_analyzer.analyze_text(description)

    cases = db.query(CaseDB).all()
    recommendations = mood_analyzer.match_cases(analysis, cases)

    return MoodAnalysisResponse(
        dominant_moods=analysis.dominant_moods,
        color_palette=analysis.color_palette,
        setting_type=analysis.setting_type,
        time_of_day=analysis.time_of_day,
        atmospheric_keywords=analysis.atmospheric_keywords,
        caption=analysis.caption,
        recommendations=recommendations,
    )


@router.post("/analyze-text", response_model=MoodAnalysisResponse)
async def analyze_mood_text(
    request: TextMoodRequest,
    db: Session = Depends(get_db),
):
    """Analyze a text description and return mood-matched cases (JSON body)."""
    analysis = await mood_analyzer.analyze_text(request.description)

    cases = db.query(CaseDB).all()
    recommendations = mood_analyzer.match_cases(analysis, cases)

    return MoodAnalysisResponse(
        dominant_moods=analysis.dominant_moods,
        color_palette=analysis.color_palette,
        setting_type=analysis.setting_type,
        time_of_day=analysis.time_of_day,
        atmospheric_keywords=analysis.atmospheric_keywords,
        caption=analysis.caption,
        recommendations=recommendations,
    )
