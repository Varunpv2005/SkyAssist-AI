from sqlalchemy.orm import Session

from incident_engine.service import IncidentLevel
from models.alert import Alert, AlertSeverity, AlertType
from models.incident import Incident
from models.ticket import Ticket, TicketPriority
from schemas.alert import AlertResponse
from websocket.manager import manager


class AlertService:
    @staticmethod
    def _generate_alert_id(db: Session) -> str:
        last = db.query(Alert).order_by(Alert.id.desc()).first()
        if not last:
            return "ALT-1001"
        last_num = int(last.alert_id.split("-")[1])
        return f"ALT-{last_num + 1}"

    @staticmethod
    def _severity_from_incident(level: IncidentLevel) -> AlertSeverity:
        mapping = {
            IncidentLevel.CRITICAL: AlertSeverity.CRITICAL,
            IncidentLevel.HIGH: AlertSeverity.HIGH,
            IncidentLevel.MEDIUM: AlertSeverity.MEDIUM,
            IncidentLevel.LOW: AlertSeverity.LOW,
        }
        return mapping.get(level, AlertSeverity.INFO)

    @staticmethod
    def _severity_from_priority(priority: TicketPriority) -> AlertSeverity:
        mapping = {
            TicketPriority.CRITICAL: AlertSeverity.CRITICAL,
            TicketPriority.HIGH: AlertSeverity.HIGH,
            TicketPriority.MEDIUM: AlertSeverity.MEDIUM,
            TicketPriority.LOW: AlertSeverity.LOW,
        }
        return mapping.get(priority, AlertSeverity.INFO)

    @staticmethod
    def _create_alert(
        db: Session,
        title: str,
        message: str,
        severity: AlertSeverity,
        alert_type: AlertType,
        reference_id: str | None = None,
    ) -> Alert:
        alert = Alert(
            alert_id=AlertService._generate_alert_id(db),
            title=title,
            message=message,
            severity=severity,
            alert_type=alert_type,
            reference_id=reference_id,
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert

    @staticmethod
    def to_broadcast(alert: Alert) -> dict:
        return {
            "event": "alert",
            "alert": AlertResponse.model_validate(alert).model_dump(mode="json"),
        }

    @staticmethod
    async def broadcast(alert: Alert) -> None:
        await manager.broadcast(AlertService.to_broadcast(alert))

    @staticmethod
    def create_incident_alert(db: Session, incident: Incident) -> Alert:
        severity = AlertService._severity_from_incident(incident.severity)
        title = f"{incident.issue_type.value} detected"
        if severity == AlertSeverity.CRITICAL:
            title = f"Critical: {title}"
        return AlertService._create_alert(
            db,
            title=title,
            message=incident.description,
            severity=severity,
            alert_type=AlertType.INCIDENT,
            reference_id=incident.incident_id,
        )

    @staticmethod
    def create_ticket_alert(db: Session, ticket: Ticket, event: str = "created") -> Alert:
        severity = AlertService._severity_from_priority(ticket.priority)
        if event == "updated":
            title = f"Ticket {ticket.ticket_id} updated"
            message = f"Status: {ticket.status.value.replace('_', ' ')}"
        else:
            title = f"Ticket {ticket.ticket_id} created"
            message = ticket.issue
        return AlertService._create_alert(
            db,
            title=title,
            message=message,
            severity=severity,
            alert_type=AlertType.TICKET,
            reference_id=ticket.ticket_id,
        )

    @staticmethod
    def list_alerts(db: Session, limit: int = 50) -> list[Alert]:
        return db.query(Alert).order_by(Alert.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_stats(db: Session) -> dict[str, int]:
        alerts = db.query(Alert).all()
        return {
            "total": len(alerts),
            "unread": sum(1 for a in alerts if not a.is_read),
            "critical": sum(1 for a in alerts if a.severity == AlertSeverity.CRITICAL),
        }

    @staticmethod
    def mark_read(db: Session, alert_id: str) -> Alert | None:
        alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
        if alert:
            alert.is_read = True
            db.commit()
            db.refresh(alert)
        return alert

    @staticmethod
    def mark_all_read(db: Session) -> int:
        count = db.query(Alert).filter(Alert.is_read.is_(False)).update({"is_read": True})
        db.commit()
        return count
