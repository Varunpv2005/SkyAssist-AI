import math
from datetime import datetime
from enum import Enum

from sqlalchemy import String, cast, func, or_
from sqlalchemy.orm import Query, Session

from database.session import engine
from incident_engine.service import IncidentLevel
from models.ai_history import AIHistory
from models.incident import Incident, IncidentStatus
from models.log_file import LogFile, LogStatus
from models.ticket import Ticket, TicketPriority, TicketStatus
from models.user import User
from schemas.search import SearchHit, SearchResponse, SearchScope, SortOrder


class SortField(str, Enum):
    CREATED_AT = "created_at"
    SEVERITY = "severity"
    STATUS = "status"
    TITLE = "title"


class SearchService:
    @staticmethod
    def _is_postgres() -> bool:
        return engine.dialect.name == "postgresql"

    @staticmethod
    def _paginate(query: Query, page: int, page_size: int) -> tuple[list, int]:
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    @staticmethod
    def _fts_filter(columns: list, query: str | None):
        if not query or not query.strip():
            return None
        q = query.strip()
        if SearchService._is_postgres():
            combined = func.concat(*[func.coalesce(c, "") for c in columns], " ")
            ts_vector = func.to_tsvector("english", combined)
            ts_query = func.plainto_tsquery("english", q)
            return ts_vector.op("@@")(ts_query)
        clauses = [cast(c, String).ilike(f"%{q}%") for c in columns]
        return or_(*clauses)

    @staticmethod
    def _apply_sort(query: Query, model, sort_by: SortField, order: SortOrder) -> Query:
        col_map = {
            SortField.CREATED_AT: model.created_at,
            SortField.SEVERITY: getattr(model, "severity", None) or getattr(model, "priority", None),
            SortField.STATUS: getattr(model, "status", None),
            SortField.TITLE: getattr(model, "issue", None) or getattr(model, "filename", None) or getattr(model, "question", None),
        }
        column = col_map.get(sort_by, model.created_at)
        if column is None:
            column = model.created_at
        return query.order_by(column.asc() if order == SortOrder.ASC else column.desc())

    @staticmethod
    def search_incidents(
        db: Session,
        query: str | None = None,
        severity: IncidentLevel | None = None,
        status: IncidentStatus | None = None,
        source: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        sort_by: SortField = SortField.CREATED_AT,
        order: SortOrder = SortOrder.DESC,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[SearchHit], int]:
        q = db.query(Incident)
        fts = SearchService._fts_filter(
            [Incident.incident_id, Incident.description, Incident.root_cause, Incident.source, Incident.recommendation],
            query,
        )
        if fts is not None:
            q = q.filter(fts)
        if severity:
            q = q.filter(Incident.severity == severity)
        if status:
            q = q.filter(Incident.status == status)
        if source:
            q = q.filter(Incident.source.ilike(f"%{source}%"))
        if date_from:
            q = q.filter(Incident.created_at >= date_from)
        if date_to:
            q = q.filter(Incident.created_at <= date_to)
        q = SearchService._apply_sort(q, Incident, sort_by, order)
        items, total = SearchService._paginate(q, page, page_size)
        hits = [
            SearchHit(
                type="incident",
                id=i.incident_id,
                title=i.incident_id,
                subtitle=i.description[:120],
                severity=i.severity.value,
                status=i.status.value,
                created_at=i.created_at,
                link=f"/incidents",
            )
            for i in items
        ]
        return hits, total

    @staticmethod
    def search_logs(
        db: Session,
        user: User,
        query: str | None = None,
        status: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        sort_by: SortField = SortField.CREATED_AT,
        order: SortOrder = SortOrder.DESC,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[SearchHit], int]:
        q = db.query(LogFile).filter(LogFile.uploaded_by == user.id)
        fts = SearchService._fts_filter([LogFile.filename, LogFile.file_type], query)
        if fts is not None:
            q = q.filter(fts)
        if status:
            try:
                log_status = LogStatus(status)
                q = q.filter(LogFile.status == log_status)
            except ValueError:
                pass
        if date_from:
            q = q.filter(LogFile.created_at >= date_from)
        if date_to:
            q = q.filter(LogFile.created_at <= date_to)
        q = SearchService._apply_sort(q, LogFile, sort_by, order)
        items, total = SearchService._paginate(q, page, page_size)
        hits = [
            SearchHit(
                type="log",
                id=str(l.id),
                title=l.filename,
                subtitle=f"{l.file_type} · {l.status.value}",
                severity=None,
                status=l.status.value,
                created_at=l.created_at,
                link="/logs",
            )
            for l in items
        ]
        return hits, total

    @staticmethod
    def search_tickets(
        db: Session,
        query: str | None = None,
        priority: TicketPriority | None = None,
        status: TicketStatus | None = None,
        assigned_to: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        sort_by: SortField = SortField.CREATED_AT,
        order: SortOrder = SortOrder.DESC,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[SearchHit], int]:
        q = db.query(Ticket)
        fts = SearchService._fts_filter(
            [Ticket.ticket_id, Ticket.issue, Ticket.root_cause, Ticket.assigned_to],
            query,
        )
        if fts is not None:
            q = q.filter(fts)
        if priority:
            q = q.filter(Ticket.priority == priority)
        if status:
            q = q.filter(Ticket.status == status)
        if assigned_to:
            q = q.filter(Ticket.assigned_to.ilike(f"%{assigned_to}%"))
        if date_from:
            q = q.filter(Ticket.created_at >= date_from)
        if date_to:
            q = q.filter(Ticket.created_at <= date_to)
        q = SearchService._apply_sort(q, Ticket, sort_by, order)
        items, total = SearchService._paginate(q, page, page_size)
        hits = [
            SearchHit(
                type="ticket",
                id=t.ticket_id,
                title=t.ticket_id,
                subtitle=t.issue[:120],
                severity=t.priority.value,
                status=t.status.value,
                created_at=t.created_at,
                link="/tickets",
            )
            for t in items
        ]
        return hits, total

    @staticmethod
    def search_ai(
        db: Session,
        user: User,
        query: str | None = None,
        severity: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        sort_by: SortField = SortField.CREATED_AT,
        order: SortOrder = SortOrder.DESC,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[SearchHit], int]:
        q = db.query(AIHistory).filter(AIHistory.user_id == user.id)
        fts = SearchService._fts_filter(
            [AIHistory.question, AIHistory.root_cause, AIHistory.explanation, AIHistory.log_snippet, AIHistory.incident_ref],
            query,
        )
        if fts is not None:
            q = q.filter(fts)
        if severity:
            q = q.filter(AIHistory.severity.ilike(f"%{severity}%"))
        if date_from:
            q = q.filter(AIHistory.created_at >= date_from)
        if date_to:
            q = q.filter(AIHistory.created_at <= date_to)
        q = SearchService._apply_sort(q, AIHistory, sort_by, order)
        items, total = SearchService._paginate(q, page, page_size)
        hits = [
            SearchHit(
                type="ai",
                id=str(h.id),
                title=h.question[:80],
                subtitle=h.root_cause[:120],
                severity=h.severity,
                status=None,
                created_at=h.created_at,
                link="/ai-assistant",
            )
            for h in items
        ]
        return hits, total

    @staticmethod
    def search(
        db: Session,
        user: User,
        scope: SearchScope = SearchScope.ALL,
        query: str | None = None,
        severity: str | None = None,
        status: str | None = None,
        source: str | None = None,
        priority: str | None = None,
        category: str | None = None,
        sort_by: SortField = SortField.CREATED_AT,
        order: SortOrder = SortOrder.DESC,
        page: int = 1,
        page_size: int = 20,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> SearchResponse:
        from services.knowledge_service import KnowledgeService

        page_size = min(max(page_size, 1), 100)
        page = max(page, 1)
        all_hits: list[SearchHit] = []
        filters = {
            "severity": severity,
            "status": status,
            "source": source,
            "priority": priority,
            "category": category,
        }

        inc_severity = IncidentLevel(severity) if severity and severity in [e.value for e in IncidentLevel] else None
        inc_status = IncidentStatus(status) if status and status in [e.value for e in IncidentStatus] else None
        tkt_priority = TicketPriority(priority) if priority and priority in [e.value for e in TicketPriority] else None
        tkt_status = TicketStatus(status) if status and status in [e.value for e in TicketStatus] else None

        if scope in (SearchScope.ALL, SearchScope.INCIDENTS):
            hits, _ = SearchService.search_incidents(
                db, query, inc_severity, inc_status, source,
                date_from=date_from, date_to=date_to,
                sort_by=sort_by, order=order, page=1, page_size=500,
            )
            all_hits.extend(hits)
        if scope in (SearchScope.ALL, SearchScope.LOGS):
            hits, _ = SearchService.search_logs(
                db, user, query, status,
                date_from=date_from, date_to=date_to,
                sort_by=sort_by, order=order, page=1, page_size=500,
            )
            all_hits.extend(hits)
        if scope in (SearchScope.ALL, SearchScope.TICKETS):
            hits, _ = SearchService.search_tickets(
                db, query, tkt_priority, tkt_status, None,
                date_from=date_from, date_to=date_to,
                sort_by=sort_by, order=order, page=1, page_size=500,
            )
            all_hits.extend(hits)
        if scope in (SearchScope.ALL, SearchScope.AI):
            hits, _ = SearchService.search_ai(
                db, user, query, severity,
                date_from=date_from, date_to=date_to,
                sort_by=sort_by, order=order, page=1, page_size=500,
            )
            all_hits.extend(hits)
        if scope in (SearchScope.ALL, SearchScope.KNOWLEDGE):
            hits, _ = KnowledgeService.search(
                db, query, category, sort_by=sort_by, order=order, page=1, page_size=500,
            )
            all_hits.extend(hits)

        if scope != SearchScope.ALL:
            total = len(all_hits)
            reverse = order == SortOrder.DESC
            all_hits.sort(key=lambda h: h.created_at, reverse=reverse)
            start = (page - 1) * page_size
            paged = all_hits[start : start + page_size]
            pages = math.ceil(total / page_size) if total else 0
            return SearchResponse(
                scope=scope, query=query, total=total, page=page,
                page_size=page_size, pages=pages, results=paged, filters=filters,
            )

        reverse = order == SortOrder.DESC
        all_hits.sort(key=lambda h: h.created_at, reverse=reverse)
        total = len(all_hits)
        start = (page - 1) * page_size
        paged = all_hits[start : start + page_size]
        pages = math.ceil(total / page_size) if total else 0
        return SearchResponse(
            scope=scope, query=query, total=total, page=page,
            page_size=page_size, pages=pages, results=paged, filters=filters,
        )
