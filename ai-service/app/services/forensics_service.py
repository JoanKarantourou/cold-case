"""
Forensics Lab Service — handles evidence analysis requests.

Uses a background thread to simulate processing time. When RabbitMQ is
available, publishes/consumes messages for async processing. Falls back
to in-process threading when RabbitMQ is unavailable.
"""

import json
import logging
import random
import threading
import time
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.db_models import EvidenceDB, ForensicRequestDB, SuspectDB

logger = logging.getLogger(__name__)

ANALYSIS_TYPES = {"FINGERPRINT", "DNA", "TOXICOLOGY", "DIGITAL", "BALLISTIC"}

# Maps evidence type to available analyses
EVIDENCE_ANALYSIS_MAP = {
    "PHYSICAL": ["FINGERPRINT", "DNA", "BALLISTIC"],
    "FORENSIC": ["DNA", "TOXICOLOGY", "FINGERPRINT"],
    "DOCUMENTARY": ["FINGERPRINT", "DIGITAL"],
    "TESTIMONIAL": ["DIGITAL"],
}

# Pre-written forensic report templates
REPORT_TEMPLATES = {
    "FINGERPRINT": (
        "═══════════════════════════════════════\n"
        "  FORENSIC FINGERPRINT ANALYSIS REPORT\n"
        "═══════════════════════════════════════\n\n"
        "SPECIMEN: {evidence_title}\n"
        "METHOD: Cyanoacrylate fuming + ninhydrin development\n"
        "ANALYST: Dr. Rebecca Chen, Forensic Lab\n\n"
        "FINDINGS:\n"
        "{findings}\n\n"
        "CONCLUSION:\n"
        "{conclusion}\n\n"
        "CLASSIFICATION: {classification}\n"
        "═══════════════════════════════════════"
    ),
    "DNA": (
        "═══════════════════════════════════════\n"
        "  FORENSIC DNA ANALYSIS REPORT\n"
        "═══════════════════════════════════════\n\n"
        "SPECIMEN: {evidence_title}\n"
        "METHOD: PCR amplification, STR profiling\n"
        "ANALYST: Dr. Marcus Webb, Molecular Biology\n\n"
        "FINDINGS:\n"
        "{findings}\n\n"
        "CONCLUSION:\n"
        "{conclusion}\n\n"
        "MATCH CONFIDENCE: {classification}\n"
        "═══════════════════════════════════════"
    ),
    "TOXICOLOGY": (
        "═══════════════════════════════════════\n"
        "  TOXICOLOGY SCREENING REPORT\n"
        "═══════════════════════════════════════\n\n"
        "SPECIMEN: {evidence_title}\n"
        "METHOD: Gas chromatography–mass spectrometry (GC-MS)\n"
        "ANALYST: Dr. Sarah Okonkwo, Toxicology\n\n"
        "FINDINGS:\n"
        "{findings}\n\n"
        "CONCLUSION:\n"
        "{conclusion}\n\n"
        "TOXICITY LEVEL: {classification}\n"
        "═══════════════════════════════════════"
    ),
    "DIGITAL": (
        "═══════════════════════════════════════\n"
        "  DIGITAL FORENSICS REPORT\n"
        "═══════════════════════════════════════\n\n"
        "SPECIMEN: {evidence_title}\n"
        "METHOD: Disk imaging, metadata analysis, data recovery\n"
        "ANALYST: Agent K. Torres, Cyber Division\n\n"
        "FINDINGS:\n"
        "{findings}\n\n"
        "CONCLUSION:\n"
        "{conclusion}\n\n"
        "DATA INTEGRITY: {classification}\n"
        "═══════════════════════════════════════"
    ),
    "BALLISTIC": (
        "═══════════════════════════════════════\n"
        "  BALLISTIC ANALYSIS REPORT\n"
        "═══════════════════════════════════════\n\n"
        "SPECIMEN: {evidence_title}\n"
        "METHOD: Comparison microscopy, trajectory analysis\n"
        "ANALYST: Sgt. David Park, Firearms Unit\n\n"
        "FINDINGS:\n"
        "{findings}\n\n"
        "CONCLUSION:\n"
        "{conclusion}\n\n"
        "MATCH STATUS: {classification}\n"
        "═══════════════════════════════════════"
    ),
}


def _generate_report(
    analysis_type: str,
    evidence: EvidenceDB,
    suspects: list[SuspectDB],
) -> str:
    """Generate a forensic report based on evidence and linked suspects."""
    template = REPORT_TEMPLATES.get(analysis_type, REPORT_TEMPLATES["FINGERPRINT"])

    linked_names = []
    for s in suspects:
        if s.id in (evidence.linked_suspect_ids or []):
            linked_names.append(s.name)

    is_red_herring = evidence.is_red_herring

    if analysis_type == "FINGERPRINT":
        if linked_names and not is_red_herring:
            findings = (
                f"Multiple latent prints recovered from the specimen.\n"
                f"After AFIS comparison, partial prints show strong correlation\n"
                f"with prints on file for: {', '.join(linked_names)}.\n"
                f"Additional unidentified prints also present — possibly contamination."
            )
            conclusion = (
                f"Evidence links specimen to {', '.join(linked_names)}.\n"
                f"This placement is inconsistent with their stated alibi."
            )
            classification = "PARTIAL MATCH — HIGH CONFIDENCE"
        else:
            findings = (
                "Latent prints recovered but heavily degraded.\n"
                "No definitive match found in the AFIS database.\n"
                "Environmental factors have compromised the specimen."
            )
            conclusion = "Inconclusive — prints too degraded for positive identification."
            classification = "INCONCLUSIVE"

    elif analysis_type == "DNA":
        if linked_names and not is_red_herring:
            findings = (
                f"Biological material recovered and amplified successfully.\n"
                f"STR profile generated with 13 loci.\n"
                f"DNA profile is consistent with: {', '.join(linked_names)}.\n"
                f"No secondary contributors detected."
            )
            conclusion = (
                f"DNA evidence places {', '.join(linked_names)} in direct contact\n"
                f"with this item. This contradicts their official statement."
            )
            classification = "99.97% MATCH PROBABILITY"
        else:
            findings = (
                "Trace biological material recovered.\n"
                "Profile generated but does not match any persons of interest.\n"
                "Possible transfer contamination from secondary source."
            )
            conclusion = "DNA does not conclusively link to any known suspect."
            classification = "NO MATCH"

    elif analysis_type == "TOXICOLOGY":
        findings = (
            "Screening conducted for 200+ substances.\n"
            "Trace amounts of sedative compound detected.\n"
            "Concentration levels suggest recent exposure."
        )
        conclusion = (
            "Presence of sedative may indicate the victim was drugged\n"
            "prior to the incident. Further investigation recommended."
        )
        classification = "TRACE LEVELS DETECTED"

    elif analysis_type == "DIGITAL":
        if linked_names and not is_red_herring:
            findings = (
                f"Data recovery performed on specimen.\n"
                f"Metadata timestamps indicate activity at critical time window.\n"
                f"Communication records reference: {', '.join(linked_names)}.\n"
                f"Deleted files partially recovered — content is suspicious."
            )
            conclusion = (
                f"Digital evidence suggests connection between this item\n"
                f"and {', '.join(linked_names)}. Timestamps contradict\n"
                f"the alibis provided."
            )
            classification = "VERIFIED — DATA INTACT"
        else:
            findings = (
                "Data recovery attempted.\n"
                "Most records have been securely wiped.\n"
                "Fragmentary data recovered but context is unclear."
            )
            conclusion = "Limited actionable intelligence recovered from specimen."
            classification = "PARTIAL RECOVERY"

    else:  # BALLISTIC
        findings = (
            "Comparison microscopy performed on specimen.\n"
            "Striation patterns analyzed and compared against database.\n"
            "Results show consistent impact patterns."
        )
        conclusion = (
            "Ballistic evidence is consistent with the weapon type\n"
            "suspected in this case. Further comparison needed."
        )
        classification = "CONSISTENT — AWAITING REFERENCE SAMPLE"

    return template.format(
        evidence_title=evidence.title,
        findings=findings,
        conclusion=conclusion,
        classification=classification,
    )


def get_available_analyses(evidence_type: str) -> list[str]:
    """Get available analysis types for a given evidence type."""
    return EVIDENCE_ANALYSIS_MAP.get(evidence_type, ["FINGERPRINT", "DIGITAL"])


def submit_forensic_request(
    db: Session,
    case_id: int,
    evidence_id: int,
    agent_id: str,
    analysis_type: str,
) -> ForensicRequestDB:
    """Submit a forensic analysis request."""
    if analysis_type not in ANALYSIS_TYPES:
        raise ValueError(f"Invalid analysis type: {analysis_type}")

    evidence = db.query(EvidenceDB).filter(
        EvidenceDB.id == evidence_id,
        EvidenceDB.case_id == case_id,
    ).first()
    if not evidence:
        raise ValueError("Evidence not found")

    # Check for duplicate pending request
    existing = db.query(ForensicRequestDB).filter(
        ForensicRequestDB.case_id == case_id,
        ForensicRequestDB.evidence_id == evidence_id,
        ForensicRequestDB.agent_id == agent_id,
        ForensicRequestDB.analysis_type == analysis_type,
        ForensicRequestDB.status == "PROCESSING",
    ).first()
    if existing:
        return existing

    estimated = random.randint(10, 30)
    request = ForensicRequestDB(
        case_id=case_id,
        evidence_id=evidence_id,
        agent_id=agent_id,
        analysis_type=analysis_type,
        status="PROCESSING",
        estimated_seconds=estimated,
    )
    db.add(request)
    db.commit()
    db.refresh(request)

    # Start background processing
    _process_in_background(request.id, case_id, evidence_id, analysis_type)

    return request


def _process_in_background(
    request_id: int,
    case_id: int,
    evidence_id: int,
    analysis_type: str,
):
    """Process forensic request in a background thread."""
    def worker():
        # Simulate processing time
        delay = random.randint(8, 20)
        time.sleep(delay)

        db = SessionLocal()
        try:
            req = db.query(ForensicRequestDB).filter(
                ForensicRequestDB.id == request_id
            ).first()
            if not req or req.status != "PROCESSING":
                return

            evidence = db.query(EvidenceDB).filter(
                EvidenceDB.id == evidence_id
            ).first()
            suspects = db.query(SuspectDB).filter(
                SuspectDB.case_id == case_id
            ).all()

            if evidence and suspects:
                report = _generate_report(analysis_type, evidence, suspects)
            else:
                report = "Analysis complete. No significant findings."

            req.status = "COMPLETE"
            req.result = report
            req.completed_at = datetime.now(timezone.utc)
            db.commit()
            logger.info(f"Forensic request {request_id} completed")
        except Exception as e:
            logger.error(f"Forensic processing error: {e}")
        finally:
            db.close()

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()


def get_forensic_request(
    db: Session, case_id: int, request_id: int
) -> Optional[ForensicRequestDB]:
    """Get a forensic request by ID."""
    return db.query(ForensicRequestDB).filter(
        ForensicRequestDB.id == request_id,
        ForensicRequestDB.case_id == case_id,
    ).first()


def get_forensic_requests_for_agent(
    db: Session, case_id: int, agent_id: str
) -> list[ForensicRequestDB]:
    """Get all forensic requests for an agent on a case."""
    return db.query(ForensicRequestDB).filter(
        ForensicRequestDB.case_id == case_id,
        ForensicRequestDB.agent_id == agent_id,
    ).all()
