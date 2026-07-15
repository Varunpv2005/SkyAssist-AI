import json
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.session import Base


class RootCauseAnalysis(Base):
    __tablename__ = "root_cause_analyses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    incident_id: Mapped[int] = mapped_column(
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    issue: Mapped[str] = mapped_column(String(255), nullable=False)
    possible_causes: Mapped[str] = mapped_column(Text, nullable=False)
    recommended_action: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    incident = relationship("Incident", back_populates="rca")

    __table_args__ = (
        Index("ix_rca_confidence_created", "confidence_score", "created_at"),
    )

    @property
    def causes_list(self) -> list[str]:
        return json.loads(self.possible_causes)

    @causes_list.setter
    def causes_list(self, value: list[str]) -> None:
        self.possible_causes = json.dumps(value)
