from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.dependencies import get_current_user
from database.session import get_db
from models.user import User
from schemas.knowledge import KnowledgeCreate, KnowledgeListResponse, KnowledgeResponse, KnowledgeUpdate
from services.knowledge_service import KnowledgeService

router = APIRouter(prefix="/knowledge", tags=["Knowledge Base"])


@router.post("", response_model=KnowledgeResponse, status_code=status.HTTP_201_CREATED)
def create_article(data: KnowledgeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    article = KnowledgeService.create(db, data, current_user)
    return KnowledgeResponse(**KnowledgeService._to_response(article))


@router.get("", response_model=KnowledgeListResponse)
def list_articles(
    category: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    articles = KnowledgeService.list_articles(db, category)
    return KnowledgeListResponse(
        total=len(articles),
        articles=[KnowledgeResponse(**KnowledgeService._to_response(a)) for a in articles],
    )


@router.get("/search")
def search_knowledge_articles(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    hits, total = KnowledgeService.search(db, q)
    if not hits:
        return {"total": 0, "articles": []}
    article_ids = [h.id for h in hits]
    articles_map = {a.article_id: a for a in KnowledgeService.list_by_ids(db, article_ids)}
    articles = [
        KnowledgeResponse(**KnowledgeService._to_response(articles_map[aid]))
        for aid in article_ids
        if aid in articles_map
    ]
    return {"total": total, "articles": articles}


@router.get("/{article_id}", response_model=KnowledgeResponse)
def get_article(article_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    article = KnowledgeService.get(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return KnowledgeResponse(**KnowledgeService._to_response(article))


@router.patch("/{article_id}", response_model=KnowledgeResponse)
def update_article(
    article_id: str, data: KnowledgeUpdate,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    article = KnowledgeService.get(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    article = KnowledgeService.update(db, article, data)
    return KnowledgeResponse(**KnowledgeService._to_response(article))


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article(article_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    article = KnowledgeService.get(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    KnowledgeService.delete(db, article)
