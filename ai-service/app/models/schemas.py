from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class CaseClassification(str, Enum):
    COLD = "COLD"
    ACTIVE = "ACTIVE"
    CLASSIFIED = "CLASSIFIED"


class EvidenceType(str, Enum):
    PHYSICAL = "PHYSICAL"
    TESTIMONIAL = "TESTIMONIAL"
    FORENSIC = "FORENSIC"
    DOCUMENTARY = "DOCUMENTARY"


class CaseFileType(str, Enum):
    CRIME_SCENE_REPORT = "CRIME_SCENE_REPORT"
    WITNESS_STATEMENT = "WITNESS_STATEMENT"
    FORENSIC_ANALYSIS = "FORENSIC_ANALYSIS"
    NEWSPAPER_CLIPPING = "NEWSPAPER_CLIPPING"
    POLICE_NOTES = "POLICE_NOTES"


class CaseBase(BaseModel):
    title: str
    case_number: str
    classification: CaseClassification
    difficulty: int = Field(ge=1, le=5)
    setting_description: str
    era: str
    mood_tags: list[str]
    crime_type: str
    synopsis: str


class CaseResponse(CaseBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CaseSummary(BaseModel):
    id: int
    title: str
    case_number: str
    classification: CaseClassification
    difficulty: int
    mood_tags: list[str]
    era: str
    synopsis: str

    model_config = {"from_attributes": True}


class SuspectBase(BaseModel):
    name: str
    age: int
    occupation: str
    relationship_to_victim: str
    personality_traits: list[str]
    alibi: str


class SuspectResponse(SuspectBase):
    id: int
    case_id: int

    model_config = {"from_attributes": True}


class SuspectFull(SuspectResponse):
    hidden_knowledge: str
    is_guilty: bool


class EvidenceBase(BaseModel):
    type: EvidenceType
    title: str
    description: str
    is_red_herring: bool = False


class EvidenceResponse(EvidenceBase):
    id: int
    case_id: int
    discovered: bool

    model_config = {"from_attributes": True}


class VictimBase(BaseModel):
    name: str
    age: int
    occupation: str
    cause_of_death: str
    background: str


class VictimResponse(VictimBase):
    id: int
    case_id: int

    model_config = {"from_attributes": True}


class CaseFileBase(BaseModel):
    type: CaseFileType
    title: str
    content: str
    classification_level: str = "STANDARD"


class CaseFileResponse(BaseModel):
    id: int
    case_id: int
    type: CaseFileType
    title: str
    classification_level: str

    model_config = {"from_attributes": True}


class CaseFileDetailResponse(CaseFileResponse):
    content: str
