from datetime import datetime

from pydantic import BaseModel, ConfigDict

from models.alert import AlertSeverity, AlertType


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    alert_id: str
    title: str
    message: str
    severity: AlertSeverity
    alert_type: AlertType
    reference_id: str | None
    is_read: bool
    created_at: datetime


class AlertListResponse(BaseModel):
    total: int
    unread: int
    alerts: list[AlertResponse]


class AlertBroadcast(BaseModel):
    event: str = "alert"
    alert: AlertResponse


class AlertStatsResponse(BaseModel):
    total: int
    unread: int
    critical: int
