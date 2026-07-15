from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RCAResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    incident_id: int
    incident_ref: str = ""
    issue: str
    possible_causes: list[str]
    recommended_action: str
    confidence_score: float = Field(..., ge=0, le=1)
    created_at: datetime


class RCAListResponse(BaseModel):
    total: int
    analyses: list[RCAResponse]


class RCAAnalyzeResponse(BaseModel):
    incident_id: str
    analysis: RCAResponse
    message: str = "Root cause analysis completed"
