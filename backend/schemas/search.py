from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class SearchScope(str, Enum):
    ALL = "all"
    INCIDENTS = "incidents"
    LOGS = "logs"
    TICKETS = "tickets"
    AI = "ai"
    KNOWLEDGE = "knowledge"


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class SearchHit(BaseModel):
    type: str
    id: str
    title: str
    subtitle: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    created_at: datetime
    link: str


class SearchResponse(BaseModel):
    scope: SearchScope
    query: Optional[str] = None
    total: int
    page: int
    page_size: int
    pages: int
    results: list[SearchHit]
    filters: dict = Field(default_factory=dict)
