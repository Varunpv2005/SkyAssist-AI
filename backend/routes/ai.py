from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ai_engine.service import AIEngine
from api.dependencies import get_current_user
from database.session import get_db
from models.user import User
from schemas.ai import (
    AIAskRequest, AIAskResponse, AIHistoryListResponse, AIHistoryResponse,
    RemediateRequest, RemediateResponse, RemediationListResponse,
)
from services.ai_service import AIService
from services.knowledge_service import KnowledgeService

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


@router.post("/ask", response_model=AIAskResponse)
async def ask_ai(
    request: AIAskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Ask the AI troubleshooting assistant a question about logs or incidents."""
    record = await AIService.ask(
        db=db,
        user=current_user,
        question=request.question,
        log_snippet=request.log_snippet,
        incident_id=request.incident_id,
        severity=request.severity,
    )
    return AIAskResponse(
        id=record.id,
        root_cause=record.root_cause,
        explanation=record.explanation,
        resolution_steps=record.steps_list,
        confidence_score=record.confidence_score,
        source=record.source,
        question=record.question,
        created_at=record.created_at,
    )


@router.get("/history", response_model=AIHistoryListResponse)
def get_ai_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get AI query history for the current user."""
    history = AIService.get_history(db, current_user)
    return AIHistoryListResponse(
        total=len(history),
        history=[
            AIHistoryResponse(**AIService.to_response(h)) for h in history
        ],
    )


@router.get("/status")
async def ai_status(current_user: User = Depends(get_current_user)):
    """Check Ollama availability and configured model."""
    return await AIEngine.check_ollama_health()


@router.post("/remediate", response_model=RemediateResponse)
async def generate_remediation(
    request: RemediateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate AI remediation recommendations for an incident."""
    record = await AIService.remediate(
        db=db,
        user=current_user,
        incident_id=request.incident_id,
        log_snippet=request.log_snippet,
        context=request.context,
    )
    return RemediateResponse(**AIService._remediation_response(record))


@router.get("/remediations", response_model=RemediationListResponse)
def get_remediation_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get remediation recommendation history."""
    records = AIService.get_remediation_history(db, current_user)
    return RemediationListResponse(
        total=len(records),
        remediations=[RemediateResponse(**AIService._remediation_response(r)) for r in records],
    )


@router.get("/remediations/{remediation_id}", response_model=RemediateResponse)
def get_remediation(
    remediation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = AIService.get_remediation(db, remediation_id, current_user)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Remediation not found")
    return RemediateResponse(**AIService._remediation_response(record))


@router.get("/knowledge")
def ai_knowledge_retrieve(
    q: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """AI knowledge retrieval from knowledge base."""
    articles = KnowledgeService.retrieve_for_ai(db, q)
    return {
        "total": len(articles),
        "articles": [
            {"article_id": a.article_id, "title": a.title, "category": a.category, "tags": a.tags_list}
            for a in articles
        ],
    }
