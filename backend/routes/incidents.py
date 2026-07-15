from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.dependencies import get_current_user
from database.session import get_db
from models.ticket import Ticket
from models.user import User
from schemas.incident import (
    DetectIncidentsResponse,
    IncidentListResponse,
    IncidentResponse,
    IncidentUpdate,
)
from services.alert_service import AlertService
from services.incident_service import IncidentService
from services.log_service import LogService

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.post("/detect/{log_id}", response_model=DetectIncidentsResponse)
def detect_incidents(
    log_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Run rule-based incident detection on a parsed log file."""
    log_file = LogService.get_log_for_user(db, log_id, current_user)

    incidents = IncidentService.detect_incidents(db, log_file, current_user)
    for incident in incidents:
        alert = AlertService.create_incident_alert(db, incident)
        background_tasks.add_task(AlertService.broadcast, alert)
        ticket = db.query(Ticket).filter(Ticket.incident_id == incident.id).first()
        if ticket:
            ticket_alert = AlertService.create_ticket_alert(db, ticket)
            background_tasks.add_task(AlertService.broadcast, ticket_alert)
    return DetectIncidentsResponse(
        log_file_id=log_file.id,
        filename=log_file.filename,
        incidents_detected=len(incidents),
        incidents=[IncidentResponse.model_validate(i) for i in incidents],
    )


@router.get("", response_model=IncidentListResponse)
def list_incidents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all detected incidents."""
    incidents = IncidentService.list_incidents(db)
    return IncidentListResponse(
        total=len(incidents),
        incidents=[IncidentResponse.model_validate(i) for i in incidents],
    )


@router.get("/stats")
def incident_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get incident summary statistics."""
    return IncidentService.get_stats(db)


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(
    incident_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single incident by ID (e.g. INC-1001)."""
    incident = IncidentService.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    return IncidentResponse.model_validate(incident)


@router.patch("/{incident_id}", response_model=IncidentResponse)
def update_incident(
    incident_id: str,
    update: IncidentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update incident status."""
    incident = IncidentService.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    if update.status:
        incident = IncidentService.update_incident(db, incident, update.status)
    return IncidentResponse.model_validate(incident)
