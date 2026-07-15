from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.dependencies import get_current_user
from database.session import get_db
from models.user import User
from schemas.ticket import (
    TicketCreate,
    TicketListResponse,
    TicketResponse,
    TicketStatsResponse,
    TicketUpdate,
)
from services.alert_service import AlertService
from services.ticket_service import TicketService

router = APIRouter(prefix="/tickets", tags=["Tickets"])


def _ticket_response(ticket) -> TicketResponse:
    return TicketResponse(**TicketService._to_response(ticket))


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(
    data: TicketCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new support ticket manually or linked to an incident."""
    ticket = TicketService.create_ticket(db, data, current_user)
    alert = AlertService.create_ticket_alert(db, ticket)
    background_tasks.add_task(AlertService.broadcast, alert)
    return _ticket_response(ticket)


@router.get("", response_model=TicketListResponse)
def list_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all support tickets."""
    tickets = TicketService.list_tickets(db)
    return TicketListResponse(
        total=len(tickets),
        tickets=[_ticket_response(t) for t in tickets],
    )


@router.get("/stats", response_model=TicketStatsResponse)
def ticket_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get ticket summary statistics."""
    return TicketStatsResponse(**TicketService.get_stats(db))


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single ticket by ID (e.g. TKT-1001)."""
    ticket = TicketService.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return _ticket_response(ticket)


@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: str,
    data: TicketUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update ticket fields or status."""
    ticket = TicketService.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    ticket = TicketService.update_ticket(db, ticket, data)
    if data.status is not None:
        alert = AlertService.create_ticket_alert(db, ticket, event="updated")
        background_tasks.add_task(AlertService.broadcast, alert)
    return _ticket_response(ticket)


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a support ticket."""
    ticket = TicketService.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    TicketService.delete_ticket(db, ticket)
