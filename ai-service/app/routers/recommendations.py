from fastapi import APIRouter

router = APIRouter(prefix="/api/ai/recommendations", tags=["recommendations"])


@router.get("")
async def recommendations_status():
    return {"message": "Recommendations endpoint - coming soon"}
