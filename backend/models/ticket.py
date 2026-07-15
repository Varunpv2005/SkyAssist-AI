import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.session import Base
from incident_engine.service import IncidentLevel


class TicketPriority(str, enum.Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


PRIORITY_FROM_SEVERITY = {
    IncidentLevel.CRITICAL: TicketPriority.CRITICAL,
    IncidentLevel.HIGH: TicketPriority.HIGH,
    IncidentLevel.MEDIUM: TicketPriority.MEDIUM,
    IncidentLevel.LOW: TicketPriority.LOW,
}


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ticket_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    issue: Mapped[str] = mapped_column(String(255), nullable=False)
    priority: Mapped[TicketPriority] = mapped_column(
        Enum(TicketPriority, name="ticket_priority", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True,
    )
    root_cause: Mapped[str] = mapped_column(Text, nullable=False)
    assigned_to: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    status: Mapped[TicketStatus] = mapped_column(
        Enum(TicketStatus, name="ticket_status", values_callable=lambda x: [e.value for e in x]),
        default=TicketStatus.OPEN,
        nullable=False,
        index=True,
    )
    incident_id: Mapped[int | None] = mapped_column(
        ForeignKey("incidents.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    incident = relationship("Incident", backref="tickets")
    creator = relationship("User", backref="tickets")

    __table_args__ = (
        Index("ix_tickets_priority_status", "priority", "status"),
    )
