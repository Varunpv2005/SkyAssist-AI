from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AIAskRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)
    log_snippet: Optional[str] = Field(None, max_length=5000)
    incident_id: Optional[str] = Field(None, max_length=20)
    severity: Optional[str] = Field(None, max_length=20)


class AIAskResponse(BaseModel):
    id: int
    root_cause: str
    explanation: str
    resolution_steps: list[str]
    confidence_score: float = Field(..., ge=0, le=1)
    source: str
    question: str
    created_at: datetime


class AIHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question: str
    log_snippet: str | None
    incident_ref: str | None
    severity: str | None
    root_cause: str
    explanation: str
    resolution_steps: list[str]
    confidence_score: float
    source: str
    created_at: datetime


class AIHistoryListResponse(BaseModel):
    total: int
    history: list[AIHistoryResponse]


class RemediateRequest(BaseModel):
    incident_id: Optional[str] = Field(None, max_length=20)
    log_snippet: Optional[str] = Field(None, max_length=5000)
    context: Optional[str] = Field(None, max_length=2000)


class RemediateResponse(BaseModel):
    id: int
    remediation_id: str
    incident_ref: str | None
    recommended_fixes: list[str]
    troubleshooting_steps: list[str]
    confidence_score: float
    source: str
    created_at: datetime


class RemediationListResponse(BaseModel):
    total: int
    remediations: list[RemediateResponse]
