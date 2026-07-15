import json

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.incident import Incident
from models.rca import RootCauseAnalysis
from rca_engine.service import analyze


class RCAService:
    @staticmethod
    def _to_response(rca: RootCauseAnalysis, incident_ref: str = "") -> dict:
        return {
            "id": rca.id,
            "incident_id": rca.incident_id,
            "incident_ref": incident_ref,
            "issue": rca.issue,
            "possible_causes": json.loads(rca.possible_causes),
            "recommended_action": rca.recommended_action,
            "confidence_score": rca.confidence_score,
            "created_at": rca.created_at,
        }

    @staticmethod
    def analyze_incident(db: Session, incident: Incident) -> RootCauseAnalysis:
        result = analyze(
            issue_type=incident.issue_type,
            severity=incident.severity,
            description=incident.description,
            source=incident.source,
        )

        existing = (
            db.query(RootCauseAnalysis)
            .filter(RootCauseAnalysis.incident_id == incident.id)
            .first()
        )

        if existing:
            existing.issue = result.issue
            existing.possible_causes = json.dumps(result.possible_causes)
            existing.recommended_action = result.recommended_action
            existing.confidence_score = result.confidence_score
            db.commit()
            db.refresh(existing)
            return existing

        rca = RootCauseAnalysis(
            incident_id=incident.id,
            issue=result.issue,
            possible_causes=json.dumps(result.possible_causes),
            recommended_action=result.recommended_action,
            confidence_score=result.confidence_score,
        )
        db.add(rca)
        db.commit()
        db.refresh(rca)
        return rca

    @staticmethod
    def get_by_incident(db: Session, incident: Incident) -> RootCauseAnalysis | None:
        return (
            db.query(RootCauseAnalysis)
            .filter(RootCauseAnalysis.incident_id == incident.id)
            .first()
        )

    @staticmethod
    def list_all(db: Session) -> list[tuple[RootCauseAnalysis, Incident]]:
        return (
            db.query(RootCauseAnalysis, Incident)
            .join(Incident, RootCauseAnalysis.incident_id == Incident.id)
            .order_by(RootCauseAnalysis.created_at.desc())
            .all()
        )

    @staticmethod
    def get_incident_or_404(db: Session, incident_id: str) -> Incident:
        incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Incident not found",
            )
        return incident
