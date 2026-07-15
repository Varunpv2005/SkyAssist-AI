import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.session import Base


class EntrySeverity(str, enum.Enum):
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"
    UNKNOWN = "UNKNOWN"


class LogEntry(Base):
    __tablename__ = "log_entries"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    log_file_id: Mapped[int] = mapped_column(ForeignKey("log_files.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    severity: Mapped[EntrySeverity] = mapped_column(
        Enum(EntrySeverity, name="entry_severity", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True,
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    log_file = relationship("LogFile", back_populates="entries")

    __table_args__ = (
        Index("ix_log_entries_severity_log_file", "severity", "log_file_id"),
    )
