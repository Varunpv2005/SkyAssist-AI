from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from incident_engine.service import IncidentLevel, IssueType
from models.incident import IncidentStatus


class IncidentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    incident_id: str
    issue_type: IssueType
    severity: IncidentLevel
    root_cause: str
    description: str
    recommendation: str
    status: IncidentStatus
    source: str | None
    log_file_id: int | None
    log_entry_id: int | None
    created_at: datetime


class IncidentListResponse(BaseModel):
    total: int
    incidents: list[IncidentResponse]


class DetectIncidentsResponse(BaseModel):
    log_file_id: int
    filename: str
    incidents_detected: int
    incidents: list[IncidentResponse]
    message: str = "Incident detection completed"


class IncidentUpdate(BaseModel):
    status: Optional[IncidentStatus] = None
