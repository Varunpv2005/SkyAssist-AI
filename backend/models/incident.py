import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.session import Base
from incident_engine.service import IncidentLevel, IssueType


class IncidentStatus(str, enum.Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    incident_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    issue_type: Mapped[IssueType] = mapped_column(
        Enum(IssueType, name="issue_type", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True,
    )
    severity: Mapped[IncidentLevel] = mapped_column(
        Enum(IncidentLevel, name="incident_level", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True,
    )
    root_cause: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[IncidentStatus] = mapped_column(
        Enum(IncidentStatus, name="incident_status", values_callable=lambda x: [e.value for e in x]),
        default=IncidentStatus.OPEN,
        nullable=False,
        index=True,
    )
    source: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    log_file_id: Mapped[int | None] = mapped_column(ForeignKey("log_files.id", ondelete="SET NULL"), nullable=True)
    log_entry_id: Mapped[int | None] = mapped_column(ForeignKey("log_entries.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    log_file = relationship("LogFile", back_populates="incidents")
    rca = relationship("RootCauseAnalysis", back_populates="incident", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_incidents_severity_status", "severity", "status"),
    )
