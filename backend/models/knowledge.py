import json
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.session import Base


class KnowledgeArticle(Base):
    __tablename__ = "knowledge_articles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    article_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    tags: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    incident_id: Mapped[int | None] = mapped_column(
        ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True, index=True,
    )
    rca_id: Mapped[int | None] = mapped_column(
        ForeignKey("root_cause_analyses.id", ondelete="SET NULL"), nullable=True, index=True,
    )
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False,
    )

    incident = relationship("Incident", backref="knowledge_articles")
    rca = relationship("RootCauseAnalysis", backref="knowledge_articles")
    author = relationship("User", backref="knowledge_articles")

    __table_args__ = (Index("ix_knowledge_category_created", "category", "created_at"),)

    @property
    def tags_list(self) -> list[str]:
        return json.loads(self.tags)

    @tags_list.setter
    def tags_list(self, value: list[str]) -> None:
        self.tags = json.dumps(value)
