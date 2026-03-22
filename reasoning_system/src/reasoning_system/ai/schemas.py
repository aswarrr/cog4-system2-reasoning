from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class FactKind(str, Enum):
    STATE = "state"
    TRANSITION = "transition"
    EVENT = "event"
    GUARD = "guard"
    ACTION = "action"
    UNKNOWN = "unknown"


class FactStatus(str, Enum):
    EXPLICIT = "explicit"
    INFERRED = "inferred"
    UNKNOWN = "unknown"


class AtomicFact(BaseModel):
    kind: FactKind = Field(..., description="The fact category")
    label: str = Field(..., description="Normalized label, e.g. insert_card")
    source_text: str = Field(..., description="Exact supporting phrase from the input")
    status: FactStatus = Field(..., description="Whether the fact is explicit, inferred, or unknown")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0")
    notes: Optional[str] = Field(default=None, description="Optional explanation")


class ExtractionResult(BaseModel):
    system_name: str = Field(..., description="Name of the system or scenario")
    facts: List[AtomicFact] = Field(default_factory=list)
    summary: Optional[str] = Field(default=None, description="Short summary of what was extracted")