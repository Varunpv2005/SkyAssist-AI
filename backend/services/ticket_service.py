from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.incident import Incident
from models.ticket import Ticket, TicketStatus
from models.user import User
from schemas.ticket import TicketCreate, TicketUpdate
from ticket_engine.service import build_ticket_from_incident


class TicketService:
    @staticmethod
    def _generate_ticket_id(db: Session) -> str:
        last = db.query(Ticket).order_by(Ticket.id.desc()).first()
        if not last:
            return "TKT-1001"
        last_num = int(last.ticket_id.split("-")[1])
        return f"TKT-{last_num + 1}"

    @staticmethod
    def _to_response(ticket: Ticket) -> dict:
        data = {
            "id": ticket.id,
            "ticket_id": ticket.ticket_id,
            "issue": ticket.issue,
            "priority": ticket.priority,
            "root_cause": ticket.root_cause,
            "assigned_to": ticket.assigned_to,
            "status": ticket.status,
            "incident_id": ticket.incident_id,
            "incident_ref": ticket.incident.incident_id if ticket.incident else None,
            "created_by": ticket.created_by,
            "created_at": ticket.created_at,
        }
        return data

    @staticmethod
    def create_ticket(db: Session, data: TicketCreate, user: User) -> Ticket:
        incident_pk: int | None = None
        if data.incident_id:
            incident = db.query(Incident).filter(Incident.incident_id == data.incident_id).first()
            if not incident:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Incident not found",
                )
            existing = db.query(Ticket).filter(Ticket.incident_id == incident.id).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ticket already exists for incident: {existing.ticket_id}",
                )
            incident_pk = incident.id

        ticket = Ticket(
            ticket_id=TicketService._generate_ticket_id(db),
            issue=data.issue,
            priority=data.priority,
            root_cause=data.root_cause,
            assigned_to=data.assigned_to,
            status=TicketStatus.OPEN,
            incident_id=incident_pk,
            created_by=user.id,
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        return ticket

    @staticmethod
    def create_from_incident(db: Session, incident: Incident, user: User) -> Ticket | None:
        existing = db.query(Ticket).filter(Ticket.incident_id == incident.id).first()
        if existing:
            return None

        draft = build_ticket_from_incident(incident)
        ticket = Ticket(
            ticket_id=TicketService._generate_ticket_id(db),
            issue=draft.issue,
            priority=draft.priority,
            root_cause=draft.root_cause,
            assigned_to=None,
            status=TicketStatus.OPEN,
            incident_id=incident.id,
            created_by=user.id,
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        return ticket

    @staticmethod
    def list_tickets(db: Session) -> list[Ticket]:
        return db.query(Ticket).order_by(Ticket.created_at.desc()).all()

    @staticmethod
    def get_ticket(db: Session, ticket_id: str) -> Ticket | None:
        return db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()

    @staticmethod
    def update_ticket(db: Session, ticket: Ticket, data: TicketUpdate) -> Ticket:
        if data.issue is not None:
            ticket.issue = data.issue
        if data.priority is not None:
            ticket.priority = data.priority
        if data.root_cause is not None:
            ticket.root_cause = data.root_cause
        if data.assigned_to is not None:
            ticket.assigned_to = data.assigned_to or None
        if data.status is not None:
            ticket.status = data.status
        db.commit()
        db.refresh(ticket)
        return ticket

    @staticmethod
    def delete_ticket(db: Session, ticket: Ticket) -> None:
        db.delete(ticket)
        db.commit()

    @staticmethod
    def get_stats(db: Session) -> dict[str, int]:
        tickets = db.query(Ticket).all()
        return {
            "total": len(tickets),
            "open": sum(1 for t in tickets if t.status == TicketStatus.OPEN),
            "in_progress": sum(1 for t in tickets if t.status == TicketStatus.IN_PROGRESS),
            "resolved": sum(1 for t in tickets if t.status == TicketStatus.RESOLVED),
            "closed": sum(1 for t in tickets if t.status == TicketStatus.CLOSED),
        }
