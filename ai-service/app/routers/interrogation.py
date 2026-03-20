"""Interrogation API endpoints — suspect interrogation powered by LangChain."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import SuspectDB, VictimDB, EvidenceDB
from app.services.interrogation_engine import interrogation_engine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai/interrogation", tags=["interrogation"])


class StartRequest(BaseModel):
    case_id: int
    suspect_id: int
    agent_id: str


class MessageRequest(BaseModel):
    case_id: int
    suspect_id: int
    agent_id: str
    message: str
    presented_evidence_ids: list[int] = []


class EndRequest(BaseModel):
    case_id: int
    suspect_id: int
    agent_id: str


def _get_suspect(db: Session, case_id: int, suspect_id: int) -> SuspectDB:
    suspect = (
        db.query(SuspectDB)
        .filter(SuspectDB.id == suspect_id, SuspectDB.case_id == case_id)
        .first()
    )
    if not suspect:
        raise HTTPException(status_code=404, detail="Suspect not found")
    return suspect


def _get_victim(db: Session, case_id: int) -> VictimDB:
    victim = db.query(VictimDB).filter(VictimDB.case_id == case_id).first()
    if not victim:
        raise HTTPException(status_code=404, detail="Case victim not found")
    return victim


def _get_evidence(db: Session, case_id: int) -> list[EvidenceDB]:
    return db.query(EvidenceDB).filter(EvidenceDB.case_id == case_id).all()


@router.post("/start")
async def start_interrogation(req: StartRequest, db: Session = Depends(get_db)):
    """Start an interrogation session with a suspect."""
    suspect = _get_suspect(db, req.case_id, req.suspect_id)
    victim = _get_victim(db, req.case_id)

    result = await interrogation_engine.start_session(
        case_id=req.case_id,
        suspect_id=req.suspect_id,
        agent_id=req.agent_id,
        suspect=suspect,
        victim=victim,
    )
    return result


@router.post("/message")
async def send_message(req: MessageRequest, db: Session = Depends(get_db)):
    """Send a message during an interrogation and receive the suspect's response."""
    suspect = _get_suspect(db, req.case_id, req.suspect_id)
    victim = _get_victim(db, req.case_id)
    all_evidence = _get_evidence(db, req.case_id)

    result = await interrogation_engine.send_message(
        case_id=req.case_id,
        suspect_id=req.suspect_id,
        agent_id=req.agent_id,
        message=req.message,
        suspect=suspect,
        victim=victim,
        all_evidence=all_evidence,
        presented_evidence_ids=req.presented_evidence_ids,
        discovered_evidence_ids=[],
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.get("/history/{case_id}/{suspect_id}/{agent_id}")
async def get_history(case_id: int, suspect_id: int, agent_id: str):
    """Get the full conversation history for an interrogation session."""
    result = interrogation_engine.get_history(case_id, suspect_id, agent_id)
    if not result:
        raise HTTPException(
            status_code=404, detail="No interrogation session found"
        )
    return result


@router.post("/end")
async def end_interrogation(req: EndRequest):
    """End an interrogation session."""
    success = interrogation_engine.end_session(
        req.case_id, req.suspect_id, req.agent_id
    )
    if not success:
        raise HTTPException(
            status_code=404, detail="No active interrogation session found"
        )
    return {"message": "Interrogation ended", "session_closed": True}
