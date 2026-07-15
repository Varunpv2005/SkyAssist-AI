from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class TimePeriod(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class TrendPoint(BaseModel):
    label: str
    count: int


class CategoryCount(BaseModel):
    category: str
    count: int


class NameValue(BaseModel):
    name: str
    value: int


class AnalyticsResponse(BaseModel):
    period: TimePeriod
    incident_trends: list[TrendPoint]
    severity_distribution: list[NameValue]
    top_error_categories: list[CategoryCount]
    resolved_vs_unresolved: list[NameValue]
    alert_frequency: list[TrendPoint]
    ticket_status: list[NameValue]
    summary: dict[str, int] = Field(default_factory=dict)
