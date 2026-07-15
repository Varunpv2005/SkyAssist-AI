from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from models.ticket import TicketPriority, TicketStatus


class TicketCreate(BaseModel):
    issue: str = Field(..., min_length=3, max_length=255)
    priority: TicketPriority = TicketPriority.MEDIUM
    root_cause: str = Field(..., min_length=3)
    assigned_to: Optional[str] = Field(None, max_length=50)
    incident_id: Optional[str] = Field(None, description="Incident ref e.g. INC-1001")


class TicketUpdate(BaseModel):
    issue: Optional[str] = Field(None, min_length=3, max_length=255)
    priority: Optional[TicketPriority] = None
    root_cause: Optional[str] = Field(None, min_length=3)
    assigned_to: Optional[str] = Field(None, max_length=50)
    status: Optional[TicketStatus] = None


class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: str
    issue: str
    priority: TicketPriority
    root_cause: str
    assigned_to: str | None
    status: TicketStatus
    incident_id: int | None
    incident_ref: str | None = None
    created_by: int
    created_at: datetime


class TicketListResponse(BaseModel):
    total: int
    tickets: list[TicketResponse]


class TicketStatsResponse(BaseModel):
    total: int
    open: int
    in_progress: int
    resolved: int
    closed: int
