import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, SessionLocal, engine, ensure_schema
from app.routers import cases, interrogation, mood, recommendations
from app.seed.seeder import seed_cases

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI):
    logger.info("Starting AI service...")
    try:
        ensure_schema()
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            seed_cases(db)
        finally:
            db.close()
    except Exception as e:
        logger.warning(f"Database initialization skipped: {e}")
    yield
    logger.info("Shutting down AI service...")


app = FastAPI(
    title="ColdCase AI Service",
    description="AI-powered mystery investigation engine",
    version="0.2.0",
    lifespan=lifespan,
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
