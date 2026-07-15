from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from api.dependencies import get_current_user
from database.session import get_db
from models.log_file import LogFile
from models.ticket import Ticket
from models.user import User
from schemas.log import LogFileResponse, LogListResponse, LogUploadResponse
from schemas.log_parser import ParseLogResponse, ParsedEntryResponse
from services.alert_service import AlertService
from services.incident_service import IncidentService
from services.log_parser_service import LogParserService
from services.log_service import LogService

router = APIRouter(prefix="/logs", tags=["Logs"])


def _emit_incident_alerts(background_tasks: BackgroundTasks, db: Session, incidents: list) -> None:
    for incident in incidents:
        alert = AlertService.create_incident_alert(db, incident)
        background_tasks.add_task(AlertService.broadcast, alert)
        ticket = db.query(Ticket).filter(Ticket.incident_id == incident.id).first()
        if ticket:
            ticket_alert = AlertService.create_ticket_alert(db, ticket)
            background_tasks.add_task(AlertService.broadcast, ticket_alert)


def _get_log_or_404(db: Session, log_id: int, user: User) -> LogFile:
    return LogService.get_log_for_user(db, log_id, user)


@router.post("/upload", response_model=LogUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_log(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a .log, .txt, or .csv file for analysis."""
    log_record = await LogService.upload_log(db, file, current_user)
    return LogUploadResponse.model_validate(log_record)


@router.get("", response_model=LogListResponse)
def list_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all uploaded log files."""
    logs = LogService.list_logs(db, current_user)
    return LogListResponse(
        total=len(logs),
        logs=[LogFileResponse.model_validate(log) for log in logs],
    )


@router.post("/{log_id}/parse", response_model=ParseLogResponse)
def parse_log(
    log_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Parse an uploaded log file and extract structured entries."""
    log_file = _get_log_or_404(db, log_id, current_user)
    entries = LogParserService.parse_log_file(db, log_file)
    created = IncidentService.detect_incidents(db, log_file, current_user)
    _emit_incident_alerts(background_tasks, db, created)
    return ParseLogResponse(
        log_file_id=log_file.id,
        filename=log_file.filename,
        total_entries=len(entries),
        entries=[ParsedEntryResponse.model_validate(e) for e in entries],
        severity_summary=LogParserService.severity_summary(entries),
    )


@router.get("/{log_id}/entries", response_model=ParseLogResponse)
def get_parsed_entries(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get previously parsed entries for a log file."""
    log_file = _get_log_or_404(db, log_id, current_user)
    entries = LogParserService.get_entries(db, log_id)
    if not entries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No parsed entries found. Run parse first.",
        )
    return ParseLogResponse(
        log_file_id=log_file.id,
        filename=log_file.filename,
        total_entries=len(entries),
        entries=[ParsedEntryResponse.model_validate(e) for e in entries],
        severity_summary=LogParserService.severity_summary(entries),
        message="Parsed entries retrieved",
    )
