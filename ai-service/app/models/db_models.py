from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from app.database import Base

SCHEMA = "ai_service"


class CaseDB(Base):
    __tablename__ = "cases"
    __table_args__ = {"schema": SCHEMA}

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    case_number = Column(String(20), unique=True, nullable=False)
    classification = Column(String(20), nullable=False, default="COLD")
    difficulty = Column(Integer, nullable=False)
    setting_description = Column(Text, nullable=False)
    era = Column(String(10), nullable=False)
    mood_tags = Column(ARRAY(String), nullable=False, default=[])
    crime_type = Column(String(50), nullable=False)
    synopsis = Column(Text, nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    suspects = relationship("SuspectDB", back_populates="case", cascade="all, delete-orphan")
    evidence = relationship("EvidenceDB", back_populates="case", cascade="all, delete-orphan")
    victims = relationship("VictimDB", back_populates="case", cascade="all, delete-orphan")
    case_files = relationship("CaseFileDB", back_populates="case", cascade="all, delete-orphan")


class SuspectDB(Base):
    __tablename__ = "suspects"
    __table_args__ = {"schema": SCHEMA}

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey(f"{SCHEMA}.cases.id"), nullable=False)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    occupation = Column(String(100), nullable=False)
    relationship_to_victim = Column(String(200), nullable=False)
    personality_traits = Column(ARRAY(String), nullable=False, default=[])
    hidden_knowledge = Column(Text, nullable=False)
    is_guilty = Column(Boolean, nullable=False, default=False)
    alibi = Column(Text, nullable=False)

    case = relationship("CaseDB", back_populates="suspects")


class EvidenceDB(Base):
    __tablename__ = "evidence"
    __table_args__ = {"schema": SCHEMA}

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey(f"{SCHEMA}.cases.id"), nullable=False)
    type = Column(String(20), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    discovered = Column(Boolean, nullable=False, default=False)
    linked_suspect_ids = Column(ARRAY(Integer), nullable=False, default=[])
    is_red_herring = Column(Boolean, nullable=False, default=False)

    case = relationship("CaseDB", back_populates="evidence")


class VictimDB(Base):
    __tablename__ = "victims"
    __table_args__ = {"schema": SCHEMA}

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey(f"{SCHEMA}.cases.id"), nullable=False)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    occupation = Column(String(100), nullable=False)
    cause_of_death = Column(String(200), nullable=False)
    background = Column(Text, nullable=False)

    case = relationship("CaseDB", back_populates="victims")


class CaseFileDB(Base):
    __tablename__ = "case_files"
    __table_args__ = {"schema": SCHEMA}

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey(f"{SCHEMA}.cases.id"), nullable=False)
    type = Column(String(30), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    classification_level = Column(String(20), nullable=False, default="STANDARD")

    case = relationship("CaseDB", back_populates="case_files")


class ForensicRequestDB(Base):
    __tablename__ = "forensic_requests"
    __table_args__ = {"schema": SCHEMA}

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey(f"{SCHEMA}.cases.id"), nullable=False)
    evidence_id = Column(Integer, ForeignKey(f"{SCHEMA}.evidence.id"), nullable=False)
    agent_id = Column(String(100), nullable=False)
    analysis_type = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, default="PROCESSING")
    result = Column(Text, nullable=True)
    estimated_seconds = Column(Integer, nullable=False, default=15)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    completed_at = Column(DateTime, nullable=True)

    case = relationship("CaseDB")
    evidence = relationship("EvidenceDB")
