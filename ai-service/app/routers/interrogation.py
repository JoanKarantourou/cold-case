from fastapi import APIRouter

router = APIRouter(prefix="/api/ai/interrogation", tags=["interrogation"])


@router.get("")
async def interrogation_status():
    return {"message": "Interrogation endpoint - coming soon"}
