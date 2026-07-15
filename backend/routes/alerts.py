from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.dependencies import get_current_user
from database.session import get_db
from models.user import User
from schemas.alert import AlertListResponse, AlertResponse, AlertStatsResponse
from services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=AlertListResponse)
def list_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List recent alerts."""
    alerts = AlertService.list_alerts(db)
    stats = AlertService.get_stats(db)
    return AlertListResponse(
        total=len(alerts),
        unread=stats["unread"],
        alerts=[AlertResponse.model_validate(a) for a in alerts],
    )


@router.get("/stats", response_model=AlertStatsResponse)
def alert_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get alert summary statistics."""
    return AlertStatsResponse(**AlertService.get_stats(db))


@router.patch("/{alert_id}/read", response_model=AlertResponse)
def mark_alert_read(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a single alert as read."""
    alert = AlertService.mark_read(db, alert_id)
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return AlertResponse.model_validate(alert)


@router.post("/read-all")
def mark_all_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark all alerts as read."""
    count = AlertService.mark_all_read(db)
    return {"marked_read": count}
