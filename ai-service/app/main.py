from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import cases, interrogation, mood, recommendations

app = FastAPI(
    title="ColdCase AI Service",
    description="AI-powered mystery investigation engine",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://localhost:5173", "http://localhost:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cases.router)
app.include_router(interrogation.router)
app.include_router(mood.router)
app.include_router(recommendations.router)


@app.get("/api/ai/health")
async def health():
    return {
        "status": "healthy",
        "service": "ai-service",
    }
