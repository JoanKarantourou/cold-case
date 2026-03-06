from fastapi import APIRouter

router = APIRouter(prefix="/api/ai/mood", tags=["mood"])


@router.get("")
async def mood_status():
    return {"message": "Mood analysis endpoint - coming soon"}
