from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    content: str = Field(..., min_length=10)
    category: str = Field(..., min_length=2, max_length=100)
    tags: list[str] = Field(default_factory=list)
    incident_id: Optional[str] = Field(None, max_length=20)
    rca_id: Optional[int] = None


class KnowledgeUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    content: Optional[str] = Field(None, min_length=10)
    category: Optional[str] = Field(None, min_length=2, max_length=100)
    tags: Optional[list[str]] = None
    incident_id: Optional[str] = None
    rca_id: Optional[int] = None


class KnowledgeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    article_id: str
    title: str
    content: str
    category: str
    tags: list[str]
    incident_id: int | None
    incident_ref: str | None = None
    rca_id: int | None
    created_by: int
    created_at: datetime
    updated_at: datetime


class KnowledgeListResponse(BaseModel):
    total: int
    articles: list[KnowledgeResponse]
