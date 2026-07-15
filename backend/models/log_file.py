import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.session import Base


class LogStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PARSED = "parsed"
    FAILED = "failed"


class LogFile(Base):
    __tablename__ = "log_files"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_type: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    status: Mapped[LogStatus] = mapped_column(
        Enum(LogStatus, name="log_status", values_callable=lambda x: [e.value for e in x]),
        default=LogStatus.UPLOADED,
        nullable=False,
        index=True,
    )
    uploaded_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    uploader = relationship("User", back_populates="log_files")
    entries = relationship("LogEntry", back_populates="log_file", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="log_file")

    __table_args__ = (
        Index("ix_log_files_status_created_at", "status", "created_at"),
    )
