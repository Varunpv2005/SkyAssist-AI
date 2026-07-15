from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from incident_engine.service import DetectedIncident, detect_from_entries
from models.incident import Incident, IncidentStatus
from models.log_entry import LogEntry
from models.log_file import LogFile, LogStatus
from models.user import User
from services.ticket_service import TicketService


class IncidentService:
    @staticmethod
    def _generate_incident_id(db: Session) -> str:
        last = db.query(Incident).order_by(Incident.id.desc()).first()
        if not last:
            return "INC-1001"
        last_num = int(last.incident_id.split("-")[1])
        return f"INC-{last_num + 1}"

    @staticmethod
    def _create_incident(
        db: Session,
        detected: DetectedIncident,
        log_file_id: int,
    ) -> Incident:
        incident = Incident(
            incident_id=IncidentService._generate_incident_id(db),
            issue_type=detected.issue_type,
            severity=detected.severity,
            root_cause=detected.root_cause,
            description=detected.description,
            recommendation=detected.recommendation,
            status=IncidentStatus.OPEN,
            source=detected.source,
            log_file_id=log_file_id,
            log_entry_id=detected.log_entry_id,
        )
        db.add(incident)
        db.commit()
        db.refresh(incident)
        return incident

    @staticmethod
    def detect_incidents(db: Session, log_file: LogFile, user: User | None = None) -> list[Incident]:
        if log_file.status != LogStatus.PARSED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Log file must be parsed before incident detection",
            )

        entries = (
            db.query(LogEntry)
            .filter(LogEntry.log_file_id == log_file.id)
            .order_by(LogEntry.line_number)
            .all()
        )

        entry_dicts = [
            {
                "id": e.id,
                "message": e.message,
                "source": e.source,
                "severity": e.severity.value,
            }
            for e in entries
        ]

        detected_list = detect_from_entries(entry_dicts)
        created: list[Incident] = []

        for detected in detected_list:
            existing = (
                db.query(Incident)
                .filter(
                    Incident.log_file_id == log_file.id,
                    Incident.issue_type == detected.issue_type,
                    Incident.source == detected.source,
                )
                .first()
            )
            if not existing:
                incident = IncidentService._create_incident(db, detected, log_file.id)
                created.append(incident)
                if user:
                    TicketService.create_from_incident(db, incident, user)

        return created

    @staticmethod
    def list_incidents(db: Session) -> list[Incident]:
        return db.query(Incident).order_by(Incident.created_at.desc()).all()

    @staticmethod
    def get_incident(db: Session, incident_id: str) -> Incident | None:
        return db.query(Incident).filter(Incident.incident_id == incident_id).first()

    @staticmethod
    def get_incident_by_pk(db: Session, pk: int) -> Incident | None:
        return db.query(Incident).filter(Incident.id == pk).first()

    @staticmethod
    def update_incident(db: Session, incident: Incident, status: IncidentStatus) -> Incident:
        incident.status = status
        db.commit()
        db.refresh(incident)
        return incident

    @staticmethod
    def get_stats(db: Session) -> dict[str, int]:
        incidents = db.query(Incident).all()
        return {
            "total": len(incidents),
            "critical": sum(1 for i in incidents if i.severity.value == "Critical"),
            "high": sum(1 for i in incidents if i.severity.value == "High"),
            "open": sum(1 for i in incidents if i.status == IncidentStatus.OPEN),
            "resolved": sum(1 for i in incidents if i.status == IncidentStatus.RESOLVED),
        }
