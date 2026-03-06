from fastapi import APIRouter

router = APIRouter(prefix="/api/ai/cases", tags=["cases"])


@router.get("")
async def list_cases():
    return {"message": "Cases endpoint - coming soon", "cases": []}
