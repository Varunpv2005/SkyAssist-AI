from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.dependencies import get_current_user
from database.session import get_db
from models.user import User
from schemas.search import SearchResponse, SearchScope, SortOrder
from services.search_service import SearchService, SortField

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("", response_model=SearchResponse)
def global_search(
    q: Optional[str] = Query(None, description="Search query"),
    scope: SearchScope = Query(SearchScope.ALL),
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    sort_by: SortField = Query(SortField.CREATED_AT),
    order: SortOrder = Query(SortOrder.DESC),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Global and scoped search with filtering, sorting, and pagination."""
    return SearchService.search(
        db, current_user, scope=scope, query=q,
        severity=severity, status=status, source=source,
        priority=priority, category=category,
        sort_by=sort_by, order=order, page=page, page_size=page_size,
        date_from=date_from, date_to=date_to,
    )
