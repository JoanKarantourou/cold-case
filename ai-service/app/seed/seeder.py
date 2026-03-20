"""Seeds the database with starter cases on application startup."""

import logging

from sqlalchemy.orm import Session

from app.models.db_models import CaseDB, SuspectDB, EvidenceDB, VictimDB, CaseFileDB
from app.seed.starter_cases import STARTER_CASES

logger = logging.getLogger(__name__)


def seed_cases(db: Session) -> None:
    existing = db.query(CaseDB).count()
    if existing > 0:
        logger.info(f"Database already has {existing} cases. Skipping seed.")
        return

    logger.info("Seeding starter cases...")

    for case_data in STARTER_CASES:
        case = CaseDB(
            title=case_data["title"],
            case_number=case_data["case_number"],
            classification=case_data["classification"],
            difficulty=case_data["difficulty"],
            setting_description=case_data["setting_description"],
            era=case_data["era"],
            mood_tags=case_data["mood_tags"],
            crime_type=case_data["crime_type"],
            synopsis=case_data["synopsis"],
        )
        db.add(case)
        db.flush()

        for victim_data in case_data["victims"]:
            db.add(VictimDB(case_id=case.id, **victim_data))

        suspect_id_map = {}
        for idx, suspect_data in enumerate(case_data["suspects"], start=1):
            suspect = SuspectDB(
                case_id=case.id,
                name=suspect_data["name"],
                age=suspect_data["age"],
                occupation=suspect_data["occupation"],
                relationship_to_victim=suspect_data["relationship_to_victim"],
                personality_traits=suspect_data["personality_traits"],
                hidden_knowledge=suspect_data["hidden_knowledge"],
                is_guilty=suspect_data["is_guilty"],
                alibi=suspect_data["alibi"],
            )
            db.add(suspect)
            db.flush()
            suspect_id_map[idx] = suspect.id

        for evidence_data in case_data["evidence"]:
            linked_ids = [
                suspect_id_map[sid]
                for sid in evidence_data["linked_suspect_ids"]
                if sid in suspect_id_map
            ]
            db.add(
                EvidenceDB(
                    case_id=case.id,
                    type=evidence_data["type"],
                    title=evidence_data["title"],
                    description=evidence_data["description"],
                    discovered=evidence_data["discovered"],
                    linked_suspect_ids=linked_ids,
                    is_red_herring=evidence_data["is_red_herring"],
                )
            )

        for file_data in case_data["case_files"]:
            db.add(
                CaseFileDB(
                    case_id=case.id,
                    type=file_data["type"],
                    title=file_data["title"],
                    content=file_data["content"],
                    classification_level=file_data["classification_level"],
                )
            )

    db.commit()
    logger.info(f"Seeded {len(STARTER_CASES)} cases successfully.")
