"""Service layer for case-related operations."""

from typing import Optional

from sqlalchemy.orm import Session

from app.models.db_models import CaseDB, SuspectDB, EvidenceDB, VictimDB, CaseFileDB


class CaseService:

    @staticmethod
    def list_cases(
        db: Session,
        mood: Optional[str] = None,
        difficulty: Optional[int] = None,
    ) -> list[CaseDB]:
        query = db.query(CaseDB)
        if difficulty is not None:
            query = query.filter(CaseDB.difficulty == difficulty)
        if mood is not None:
            query = query.filter(CaseDB.mood_tags.any(mood))
        return query.all()

    @staticmethod
    def get_case(db: Session, case_id: int) -> Optional[CaseDB]:
        return db.query(CaseDB).filter(CaseDB.id == case_id).first()

    @staticmethod
    def get_case_files(db: Session, case_id: int) -> list[CaseFileDB]:
        return db.query(CaseFileDB).filter(CaseFileDB.case_id == case_id).all()

    @staticmethod
    def get_case_file(db: Session, case_id: int, file_id: int) -> Optional[CaseFileDB]:
        return (
            db.query(CaseFileDB)
            .filter(CaseFileDB.case_id == case_id, CaseFileDB.id == file_id)
            .first()
        )

    @staticmethod
    def get_suspects(db: Session, case_id: int) -> list[SuspectDB]:
        return db.query(SuspectDB).filter(SuspectDB.case_id == case_id).all()

    @staticmethod
    def get_evidence(db: Session, case_id: int) -> list[EvidenceDB]:
        return db.query(EvidenceDB).filter(EvidenceDB.case_id == case_id).all()

    @staticmethod
    def get_discovered_evidence(
        db: Session, case_id: int, discovered_ids: list[int]
    ) -> list[EvidenceDB]:
        return (
            db.query(EvidenceDB)
            .filter(EvidenceDB.case_id == case_id, EvidenceDB.id.in_(discovered_ids))
            .all()
        )

    @staticmethod
    def get_victims(db: Session, case_id: int) -> list[VictimDB]:
        return db.query(VictimDB).filter(VictimDB.case_id == case_id).all()
