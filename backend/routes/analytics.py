from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.dependencies import get_current_user
from database.session import get_db
from models.user import User
from schemas.analytics import AnalyticsResponse, TimePeriod
from services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("", response_model=AnalyticsResponse)
def get_analytics(
    period: TimePeriod = Query(TimePeriod.DAILY, description="daily, weekly, or monthly"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get aggregated analytics for charts and dashboards."""
    return AnalyticsService.get_analytics(db, period)
