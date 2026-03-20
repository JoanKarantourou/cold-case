"""
Case Scoring Service — evaluates agent submissions and scores their investigation.

Rank tiers:
  ROOKIE (0-30), DETECTIVE (31-50), SENIOR DETECTIVE (51-70),
  SPECIAL AGENT (71-85), CHIEF INVESTIGATOR (86-100)
"""

import logging
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.db_models import CaseDB, EvidenceDB, SuspectDB, VictimDB

logger = logging.getLogger(__name__)

RANK_TIERS = [
    (0, 30, "ROOKIE"),
    (31, 50, "DETECTIVE"),
    (51, 70, "SENIOR DETECTIVE"),
    (71, 85, "SPECIAL AGENT"),
    (86, 100, "CHIEF INVESTIGATOR"),
]


def _get_rank(score: int) -> str:
    for low, high, rank in RANK_TIERS:
        if low <= score <= high:
            return rank
    return "ROOKIE"


def _simple_text_similarity(text_a: str, text_b: str) -> float:
    """Simple keyword overlap similarity (0.0 to 1.0) as LLM-free fallback."""
    if not text_a or not text_b:
        return 0.0

    stop_words = {
        "the", "a", "an", "is", "was", "were", "are", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "to", "of", "in", "for",
        "on", "with", "at", "by", "from", "as", "into", "about", "between",
        "through", "during", "before", "after", "and", "but", "or", "not",
        "no", "so", "if", "then", "than", "that", "this", "it", "he", "she",
        "they", "them", "his", "her", "their", "its", "who", "which", "what",
    }

    words_a = {
        w.lower().strip(".,!?;:\"'")
        for w in text_a.split()
        if len(w) > 2 and w.lower() not in stop_words
    }
    words_b = {
        w.lower().strip(".,!?;:\"'")
        for w in text_b.split()
        if len(w) > 2 and w.lower() not in stop_words
    }

    if not words_a or not words_b:
        return 0.0

    overlap = words_a & words_b
    union = words_a | words_b

    return len(overlap) / len(union) if union else 0.0


def _build_solution_narrative(
    case: CaseDB,
    guilty_suspect: SuspectDB,
    victim: VictimDB,
) -> str:
    """Build the full solution narrative for case reveal."""
    return (
        f"═══════════════════════════════════════\n"
        f"  CLASSIFIED: FULL CASE SOLUTION\n"
        f"  {case.case_number} — {case.title.upper()}\n"
        f"═══════════════════════════════════════\n\n"
        f"VICTIM: {victim.name}, age {victim.age}\n"
        f"Cause of death: {victim.cause_of_death}\n\n"
        f"THE KILLER: {guilty_suspect.name}\n"
        f"Occupation: {guilty_suspect.occupation}\n"
        f"Relationship: {guilty_suspect.relationship_to_victim}\n\n"
        f"WHAT REALLY HAPPENED:\n"
        f"{guilty_suspect.hidden_knowledge}\n\n"
        f"MOTIVE:\n"
        f"As the victim's {guilty_suspect.relationship_to_victim.lower()}, "
        f"{guilty_suspect.name} had both the means and the opportunity. "
        f"Their personality traits ({', '.join(guilty_suspect.personality_traits or [])}) "
        f"played directly into the events of that night.\n\n"
        f"Their alibi — \"{guilty_suspect.alibi}\" — was fabricated to cover "
        f"their involvement.\n\n"
        f"═══════════════════════════════════════\n"
        f"  CASE CLOSED\n"
        f"═══════════════════════════════════════"
    )


def evaluate_submission(
    db: Session,
    case_id: int,
    accused_suspect_id: int,
    motive: str,
    method: str,
    key_evidence_ids: list[int],
    timeline_of_events: str,
) -> dict:
    """Evaluate a case submission and return scoring breakdown."""
    case = db.query(CaseDB).filter(CaseDB.id == case_id).first()
    if not case:
        raise ValueError("Case not found")

    suspects = db.query(SuspectDB).filter(SuspectDB.case_id == case_id).all()
    all_evidence = db.query(EvidenceDB).filter(EvidenceDB.case_id == case_id).all()
    victim = db.query(VictimDB).filter(VictimDB.case_id == case_id).first()

    guilty_suspect = next((s for s in suspects if s.is_guilty), None)
    if not guilty_suspect:
        raise ValueError("Case has no guilty suspect defined")

    # 1. Correct killer? (40 points max)
    correct_killer = accused_suspect_id == guilty_suspect.id
    killer_score = 40 if correct_killer else 0

    # 2. Motive accuracy (20 points max)
    actual_motive = guilty_suspect.hidden_knowledge
    motive_similarity = _simple_text_similarity(motive, actual_motive)
    # Also check against method/timeline for partial credit
    combined_submission = f"{motive} {method} {timeline_of_events}"
    combined_similarity = _simple_text_similarity(combined_submission, actual_motive)
    motive_accuracy = max(motive_similarity, combined_similarity)
    motive_score = round(motive_accuracy * 20)

    # 3. Evidence quality (20 points max)
    key_non_herring = [e for e in all_evidence if not e.is_red_herring]
    cited_key = [e for e in key_non_herring if e.id in key_evidence_ids]
    evidence_ratio = len(cited_key) / len(key_non_herring) if key_non_herring else 0
    evidence_score = round(evidence_ratio * 20)

    # 4. Red herring penalty (-10 per red herring cited)
    red_herrings_cited = [e for e in all_evidence if e.is_red_herring and e.id in key_evidence_ids]
    red_herring_penalty = len(red_herrings_cited) * 10

    # 5. Discovery rate (10 points max)
    total_evidence = len(all_evidence)
    discovered_evidence = [e for e in all_evidence if e.discovered]
    discovery_rate = len(discovered_evidence) / total_evidence if total_evidence else 0
    discovery_score = round(discovery_rate * 10)

    # 6. Bonus for timeline quality (10 points max)
    timeline_score = 0
    if timeline_of_events and len(timeline_of_events) > 50:
        timeline_similarity = _simple_text_similarity(timeline_of_events, actual_motive)
        timeline_score = round(timeline_similarity * 10)

    # Overall
    overall_score = max(0, min(100,
        killer_score + motive_score + evidence_score
        - red_herring_penalty + discovery_score + timeline_score
    ))
    rank_earned = _get_rank(overall_score)

    # Build feedback
    feedback_lines = []
    if correct_killer:
        feedback_lines.append(
            f"You correctly identified {guilty_suspect.name} as the perpetrator."
        )
    else:
        accused = next((s for s in suspects if s.id == accused_suspect_id), None)
        accused_name = accused.name if accused else "an unknown suspect"
        feedback_lines.append(
            f"You accused {accused_name}, but the actual perpetrator was {guilty_suspect.name}."
        )

    if motive_accuracy > 0.6:
        feedback_lines.append("Your understanding of the motive was strong.")
    elif motive_accuracy > 0.3:
        feedback_lines.append("You partially grasped the motive, but missed key details.")
    else:
        feedback_lines.append("Your stated motive was largely inaccurate.")

    if evidence_ratio > 0.7:
        feedback_lines.append(
            f"Excellent evidence work — you cited {len(cited_key)} of "
            f"{len(key_non_herring)} key evidence items."
        )
    elif evidence_ratio > 0.4:
        feedback_lines.append(
            f"You found some key evidence ({len(cited_key)}/{len(key_non_herring)}) "
            f"but missed important pieces."
        )
    else:
        feedback_lines.append("You missed most of the key evidence in your report.")

    if red_herrings_cited:
        feedback_lines.append(
            f"Warning: You included {len(red_herrings_cited)} red herring(s) "
            f"as key evidence, costing you {red_herring_penalty} points."
        )

    # Build solution narrative
    full_solution = _build_solution_narrative(case, guilty_suspect, victim) if victim else ""

    return {
        "correct_killer": correct_killer,
        "motive_accuracy": round(motive_accuracy, 2),
        "evidence_score": round(evidence_ratio, 2),
        "red_herring_penalty": red_herring_penalty,
        "discovery_rate": round(discovery_rate, 2),
        "overall_score": overall_score,
        "rank_earned": rank_earned,
        "feedback": " ".join(feedback_lines),
        "full_solution": full_solution,
    }
