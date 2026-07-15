from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.dependencies import get_current_user
from database.session import get_db
from models.user import User
from schemas.rca import RCAAnalyzeResponse, RCAListResponse, RCAResponse
from services.rca_service import RCAService

router = APIRouter(prefix="/analysis", tags=["Root Cause Analysis"])


@router.post("/incident/{incident_id}", response_model=RCAAnalyzeResponse)
def analyze_incident(
    incident_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Run rule-based root cause analysis on an incident."""
    incident = RCAService.get_incident_or_404(db, incident_id)
    rca = RCAService.analyze_incident(db, incident)
    analysis = RCAResponse(
        id=rca.id,
        incident_id=rca.incident_id,
        incident_ref=incident.incident_id,
        issue=rca.issue,
        possible_causes=rca.causes_list,
        recommended_action=rca.recommended_action,
        confidence_score=rca.confidence_score,
        created_at=rca.created_at,
    )
    return RCAAnalyzeResponse(incident_id=incident_id, analysis=analysis)


@router.get("/incident/{incident_id}", response_model=RCAResponse)
def get_analysis(
    incident_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get root cause analysis for an incident."""
    incident = RCAService.get_incident_or_404(db, incident_id)
    rca = RCAService.get_by_incident(db, incident)
    if not rca:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found. Run analysis first.",
        )
    return RCAResponse(
        id=rca.id,
        incident_id=rca.incident_id,
        incident_ref=incident.incident_id,
        issue=rca.issue,
        possible_causes=rca.causes_list,
        recommended_action=rca.recommended_action,
        confidence_score=rca.confidence_score,
        created_at=rca.created_at,
    )


@router.get("", response_model=RCAListResponse)
def list_analyses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all completed root cause analyses."""
    results = RCAService.list_all(db)
    analyses = [
        RCAResponse(
            id=rca.id,
            incident_id=rca.incident_id,
            incident_ref=incident.incident_id,
            issue=rca.issue,
            possible_causes=rca.causes_list,
            recommended_action=rca.recommended_action,
            confidence_score=rca.confidence_score,
            created_at=rca.created_at,
        )
        for rca, incident in results
    ]
    return RCAListResponse(total=len(analyses), analyses=analyses)
