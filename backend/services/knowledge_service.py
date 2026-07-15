from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.incident import Incident
from models.knowledge import KnowledgeArticle
from models.rca import RootCauseAnalysis
from models.user import User
from schemas.knowledge import KnowledgeCreate, KnowledgeUpdate
from schemas.search import SearchHit
from services.search_service import SearchService, SortField, SortOrder


class KnowledgeService:
    @staticmethod
    def _generate_id(db: Session) -> str:
        last = db.query(KnowledgeArticle).order_by(KnowledgeArticle.id.desc()).first()
        if not last:
            return "KB-1001"
        return f"KB-{int(last.article_id.split('-')[1]) + 1}"

    @staticmethod
    def _to_response(article: KnowledgeArticle) -> dict:
        return {
            "id": article.id,
            "article_id": article.article_id,
            "title": article.title,
            "content": article.content,
            "category": article.category,
            "tags": article.tags_list,
            "incident_id": article.incident_id,
            "incident_ref": article.incident.incident_id if article.incident else None,
            "rca_id": article.rca_id,
            "created_by": article.created_by,
            "created_at": article.created_at,
            "updated_at": article.updated_at,
        }

    @staticmethod
    def create(db: Session, data: KnowledgeCreate, user: User) -> KnowledgeArticle:
        incident_pk = None
        if data.incident_id:
            inc = db.query(Incident).filter(Incident.incident_id == data.incident_id).first()
            if not inc:
                raise HTTPException(status_code=404, detail="Incident not found")
            incident_pk = inc.id
        if data.rca_id:
            rca = db.query(RootCauseAnalysis).filter(RootCauseAnalysis.id == data.rca_id).first()
            if not rca:
                raise HTTPException(status_code=404, detail="RCA not found")

        article = KnowledgeArticle(
            article_id=KnowledgeService._generate_id(db),
            title=data.title,
            content=data.content,
            category=data.category,
            incident_id=incident_pk,
            rca_id=data.rca_id,
            created_by=user.id,
        )
        article.tags_list = data.tags
        db.add(article)
        db.commit()
        db.refresh(article)
        return article

    @staticmethod
    def list_articles(db: Session, category: str | None = None) -> list[KnowledgeArticle]:
        q = db.query(KnowledgeArticle)
        if category:
            q = q.filter(KnowledgeArticle.category == category)
        return q.order_by(KnowledgeArticle.updated_at.desc()).all()

    @staticmethod
    def get(db: Session, article_id: str) -> KnowledgeArticle | None:
        return db.query(KnowledgeArticle).filter(KnowledgeArticle.article_id == article_id).first()

    @staticmethod
    def list_by_ids(db: Session, article_ids: list[str]) -> list[KnowledgeArticle]:
        if not article_ids:
            return []
        return db.query(KnowledgeArticle).filter(KnowledgeArticle.article_id.in_(article_ids)).all()

    @staticmethod
    def update(db: Session, article: KnowledgeArticle, data: KnowledgeUpdate) -> KnowledgeArticle:
        if data.title is not None:
            article.title = data.title
        if data.content is not None:
            article.content = data.content
        if data.category is not None:
            article.category = data.category
        if data.tags is not None:
            article.tags_list = data.tags
        if data.incident_id is not None:
            if data.incident_id == "":
                article.incident_id = None
            else:
                inc = db.query(Incident).filter(Incident.incident_id == data.incident_id).first()
                if not inc:
                    raise HTTPException(status_code=404, detail="Incident not found")
                article.incident_id = inc.id
        if data.rca_id is not None:
            if data.rca_id == 0:
                article.rca_id = None
            else:
                rca = db.query(RootCauseAnalysis).filter(RootCauseAnalysis.id == data.rca_id).first()
                if not rca:
                    raise HTTPException(status_code=404, detail="RCA not found")
                article.rca_id = data.rca_id
        db.commit()
        db.refresh(article)
        return article

    @staticmethod
    def delete(db: Session, article: KnowledgeArticle) -> None:
        db.delete(article)
        db.commit()

    @staticmethod
    def search(
        db: Session,
        query: str | None = None,
        category: str | None = None,
        sort_by: SortField = SortField.CREATED_AT,
        order: SortOrder = SortOrder.DESC,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[SearchHit], int]:
        q = db.query(KnowledgeArticle)
        fts = SearchService._fts_filter(
            [KnowledgeArticle.title, KnowledgeArticle.content, KnowledgeArticle.category, KnowledgeArticle.article_id],
            query,
        )
        if fts is not None:
            q = q.filter(fts)
        if category:
            q = q.filter(KnowledgeArticle.category == category)
        if sort_by == SortField.TITLE:
            q = q.order_by(KnowledgeArticle.title.asc() if order == SortOrder.ASC else KnowledgeArticle.title.desc())
        else:
            q = q.order_by(KnowledgeArticle.created_at.asc() if order == SortOrder.ASC else KnowledgeArticle.created_at.desc())
        items, total = SearchService._paginate(q, page, page_size)
        hits = [
            SearchHit(
                type="knowledge",
                id=a.article_id,
                title=a.title,
                subtitle=a.category,
                severity=None,
                status=None,
                created_at=a.created_at,
                link="/knowledge",
            )
            for a in items
        ]
        return hits, total

    @staticmethod
    def retrieve_for_ai(db: Session, query: str, limit: int = 3) -> list[KnowledgeArticle]:
        hits, _ = KnowledgeService.search(db, query=query, page_size=limit)
        if not hits:
            return []
        ids = [h.id for h in hits]
        articles = db.query(KnowledgeArticle).filter(KnowledgeArticle.article_id.in_(ids)).limit(limit).all()
        return articles
