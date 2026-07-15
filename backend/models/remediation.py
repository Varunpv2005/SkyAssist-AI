import json
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.session import Base


class Remediation(Base):
    __tablename__ = "remediations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    remediation_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    incident_id: Mapped[int | None] = mapped_column(
        ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True, index=True,
    )
    incident_ref: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    recommended_fixes: Mapped[str] = mapped_column(Text, nullable=False)
    troubleshooting_steps: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(20), nullable=False, default="fallback")
    context: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )

    incident = relationship("Incident", backref="remediations")
    author = relationship("User", backref="remediations")

    __table_args__ = (Index("ix_remediation_incident_created", "incident_id", "created_at"),)

    @property
    def fixes_list(self) -> list[str]:
        return json.loads(self.recommended_fixes)

    @property
    def steps_list(self) -> list[str]:
        return json.loads(self.troubleshooting_steps)
