import json

from sqlalchemy.orm import Session

from ai_engine.service import AIEngine
from models.ai_history import AIHistory
from models.remediation import Remediation
from models.user import User
from services.incident_service import IncidentService
from services.knowledge_service import KnowledgeService


class AIService:
    @staticmethod
    async def ask(
        db: Session,
        user: User,
        question: str,
        log_snippet: str | None = None,
        incident_id: str | None = None,
        severity: str | None = None,
    ) -> AIHistory:
        incident_details = "None"
        severity = severity or "Unknown"
        if incident_id:
            incident = IncidentService.get_incident(db, incident_id)
            if incident:
                incident_details = (
                    f"{incident.incident_id} — {incident.issue_type.value}: "
                    f"{incident.description}"
                )
                if not severity or severity == "Unknown":
                    severity = incident.severity.value
                if not log_snippet and incident.description:
                    log_snippet = incident.description

        kb_articles = KnowledgeService.retrieve_for_ai(db, question)
        if kb_articles:
            kb_text = "\n".join(f"[{a.title}] {a.content[:300]}" for a in kb_articles)
            log_snippet = f"{log_snippet or ''}\n\nKnowledge base:\n{kb_text}".strip()

        result = await AIEngine.analyze(
            question=question,
            log_snippet=log_snippet or "",
            incident_details=incident_details,
            severity=severity or "Unknown",
        )

        record = AIHistory(
            user_id=user.id,
            question=question,
            log_snippet=log_snippet,
            incident_ref=incident_id,
            severity=severity,
            root_cause=result.root_cause,
            explanation=result.explanation,
            resolution_steps=json.dumps(result.resolution_steps),
            confidence_score=result.confidence_score,
            source=result.source,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def get_history(db: Session, user: User) -> list[AIHistory]:
        return (
            db.query(AIHistory)
            .filter(AIHistory.user_id == user.id)
            .order_by(AIHistory.created_at.desc())
            .all()
        )

    @staticmethod
    def to_response(record: AIHistory) -> dict:
        return {
            "id": record.id,
            "question": record.question,
            "log_snippet": record.log_snippet,
            "incident_ref": record.incident_ref,
            "severity": record.severity,
            "root_cause": record.root_cause,
            "explanation": record.explanation,
            "resolution_steps": record.steps_list,
            "confidence_score": record.confidence_score,
            "source": record.source,
            "created_at": record.created_at,
        }

    @staticmethod
    def _generate_remediation_id(db: Session) -> str:
        last = db.query(Remediation).order_by(Remediation.id.desc()).first()
        if not last:
            return "REM-1001"
        return f"REM-{int(last.remediation_id.split('-')[1]) + 1}"

    @staticmethod
    def _remediation_response(record: Remediation) -> dict:
        return {
            "id": record.id,
            "remediation_id": record.remediation_id,
            "incident_ref": record.incident_ref,
            "recommended_fixes": record.fixes_list,
            "troubleshooting_steps": record.steps_list,
            "confidence_score": record.confidence_score,
            "source": record.source,
            "created_at": record.created_at,
        }

    @staticmethod
    async def remediate(
        db: Session,
        user: User,
        incident_id: str | None = None,
        log_snippet: str | None = None,
        context: str | None = None,
    ) -> Remediation:
        incident_details = context or "General security remediation request"
        severity = "Unknown"
        incident_pk = None
        incident_ref = None

        if incident_id:
            incident = IncidentService.get_incident(db, incident_id)
            if not incident:
                from fastapi import HTTPException, status
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
            incident_pk = incident.id
            incident_ref = incident.incident_id
            incident_details = f"{incident.incident_id} — {incident.issue_type.value}: {incident.description}"
            severity = incident.severity.value
            if not log_snippet:
                log_snippet = incident.description

        kb_articles = KnowledgeService.retrieve_for_ai(db, incident_details)
        knowledge_context = (
            "\n".join(f"- {a.title}: {a.content[:400]}" for a in kb_articles)
            if kb_articles else "None"
        )

        result = await AIEngine.generate_remediation(
            incident_details=incident_details,
            severity=severity,
            log_snippet=log_snippet or "",
            knowledge_context=knowledge_context,
        )

        record = Remediation(
            remediation_id=AIService._generate_remediation_id(db),
            incident_id=incident_pk,
            incident_ref=incident_ref,
            recommended_fixes=json.dumps(result.recommended_fixes),
            troubleshooting_steps=json.dumps(result.troubleshooting_steps),
            confidence_score=result.confidence_score,
            source=result.source,
            context=context,
            created_by=user.id,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def get_remediation_history(db: Session, user: User) -> list[Remediation]:
        return (
            db.query(Remediation)
            .filter(Remediation.created_by == user.id)
            .order_by(Remediation.created_at.desc())
            .all()
        )

    @staticmethod
    def get_remediation(db: Session, remediation_id: str, user: User) -> Remediation | None:
        return (
            db.query(Remediation)
            .filter(
                Remediation.remediation_id == remediation_id,
                Remediation.created_by == user.id,
            )
            .first()
        )
