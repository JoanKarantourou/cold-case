from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schemas import (
    CaseFileDetailResponse,
    CaseFileResponse,
    CaseResponse,
    CaseSummary,
    EvidenceResponse,
    SuspectResponse,
    VictimResponse,
)
from app.services.case_service import CaseService
from app.services.forensics_service import (
    get_available_analyses,
    get_forensic_request,
    get_forensic_requests_for_agent,
    submit_forensic_request,
)

router = APIRouter(prefix="/api/ai/cases", tags=["cases"])


@router.get("", response_model=list[CaseSummary])
async def list_cases(
    mood: Optional[str] = Query(None),
    difficulty: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    cases = CaseService.list_cases(db, mood=mood, difficulty=difficulty)
    return [
        CaseSummary(
            id=c.id,
            title=c.title,
            case_number=c.case_number,
            classification=c.classification,
            difficulty=c.difficulty,
            mood_tags=c.mood_tags,
            era=c.era,
            synopsis=c.synopsis,
        )
        for c in cases
    ]


@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(case_id: int, db: Session = Depends(get_db)):
    case = CaseService.get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.get("/{case_id}/files", response_model=list[CaseFileResponse])
async def get_case_files(case_id: int, db: Session = Depends(get_db)):
    case = CaseService.get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return CaseService.get_case_files(db, case_id)


@router.get("/{case_id}/files/{file_id}", response_model=CaseFileDetailResponse)
async def get_case_file(case_id: int, file_id: int, db: Session = Depends(get_db)):
    case_file = CaseService.get_case_file(db, case_id, file_id)
    if not case_file:
        raise HTTPException(status_code=404, detail="Case file not found")
    return case_file


@router.get("/{case_id}/suspects", response_model=list[SuspectResponse])
async def get_suspects(case_id: int, db: Session = Depends(get_db)):
    case = CaseService.get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return CaseService.get_suspects(db, case_id)


@router.get("/{case_id}/victims", response_model=list[VictimResponse])
async def get_victims(case_id: int, db: Session = Depends(get_db)):
    case = CaseService.get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return CaseService.get_victims(db, case_id)


@router.get("/{case_id}/evidence", response_model=list[EvidenceResponse])
async def get_evidence(
    case_id: int,
    agent_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    case = CaseService.get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    all_evidence = CaseService.get_evidence(db, case_id)
    return [
        EvidenceResponse(
            id=e.id,
            case_id=e.case_id,
            type=e.type,
            title=e.title if e.discovered else "[REDACTED]",
            description=e.description if e.discovered else "[████████████]",
            discovered=e.discovered,
            is_red_herring=False,
        )
        for e in all_evidence
    ]


# ── Forensics Lab ─────────────────────────────────────────


class ForensicSubmitRequest(BaseModel):
    evidence_id: int
    analysis_type: str
    agent_id: str


@router.post("/{case_id}/forensics/submit")
async def submit_forensics(
    case_id: int,
    req: ForensicSubmitRequest,
    db: Session = Depends(get_db),
):
    """Submit evidence for forensic analysis."""
    case = CaseService.get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    try:
        forensic_req = submit_forensic_request(
            db, case_id, req.evidence_id, req.agent_id, req.analysis_type
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "request_id": forensic_req.id,
        "status": forensic_req.status,
        "analysis_type": forensic_req.analysis_type,
        "estimated_time_seconds": forensic_req.estimated_seconds,
    }


@router.get("/{case_id}/forensics/{request_id}")
async def get_forensics_status(
    case_id: int,
    request_id: int,
    db: Session = Depends(get_db),
):
    """Check status of a forensic analysis request."""
    req = get_forensic_request(db, case_id, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Forensic request not found")

    return {
        "request_id": req.id,
        "evidence_id": req.evidence_id,
        "analysis_type": req.analysis_type,
        "status": req.status,
        "estimated_time_seconds": req.estimated_seconds,
        "result": req.result,
        "created_at": req.created_at.isoformat() if req.created_at else None,
        "completed_at": req.completed_at.isoformat() if req.completed_at else None,
    }


@router.get("/{case_id}/forensics")
async def list_forensic_requests(
    case_id: int,
    agent_id: str = Query(...),
    db: Session = Depends(get_db),
):
    """List all forensic requests for an agent on a case."""
    requests = get_forensic_requests_for_agent(db, case_id, agent_id)
    return [
        {
            "request_id": r.id,
            "evidence_id": r.evidence_id,
            "analysis_type": r.analysis_type,
            "status": r.status,
            "estimated_time_seconds": r.estimated_seconds,
            "result": r.result,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "completed_at": r.completed_at.isoformat() if r.completed_at else None,
        }
        for r in requests
    ]
