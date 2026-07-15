from collections import defaultdict
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from incident_engine.service import IssueType
from models.alert import Alert
from models.incident import Incident, IncidentStatus
from models.ticket import Ticket, TicketStatus
from schemas.analytics import AnalyticsResponse, CategoryCount, NameValue, TimePeriod, TrendPoint

ISSUE_LABELS: dict[IssueType, str] = {
    IssueType.AUTH_FAILURE: "Auth Failure",
    IssueType.TOKEN_EXPIRED: "Token Expired",
    IssueType.API_TIMEOUT: "API Timeout",
    IssueType.DATABASE_CONNECTION_ERROR: "DB Connection",
    IssueType.SSL_HANDSHAKE_FAILURE: "SSL Handshake",
    IssueType.EMAIL_DELIVERY_FAILURE: "Email Delivery",
    IssueType.NETWORK_ERROR: "Network Error",
    IssueType.DNS_ERROR: "DNS Error",
}


class AnalyticsService:
    @staticmethod
    def _utc_now() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def _ensure_aware(dt: datetime) -> datetime:
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    @staticmethod
    def _since(period: TimePeriod) -> datetime:
        now = AnalyticsService._utc_now()
        if period == TimePeriod.DAILY:
            return now - timedelta(days=7)
        if period == TimePeriod.WEEKLY:
            return now - timedelta(weeks=8)
        return now - timedelta(days=180)

    @staticmethod
    def _bucket_labels(period: TimePeriod) -> list[str]:
        now = AnalyticsService._utc_now()
        labels: list[str] = []
        if period == TimePeriod.DAILY:
            for i in range(6, -1, -1):
                labels.append((now - timedelta(days=i)).strftime("%Y-%m-%d"))
        elif period == TimePeriod.WEEKLY:
            for i in range(7, -1, -1):
                d = now - timedelta(weeks=i)
                labels.append(f"{d.isocalendar()[0]}-W{d.isocalendar()[1]:02d}")
        else:
            year, month = now.year, now.month
            for _ in range(6):
                labels.append(f"{year}-{month:02d}")
                month -= 1
                if month == 0:
                    month = 12
                    year -= 1
            labels.reverse()
        return labels

    @staticmethod
    def _bucket_key(dt: datetime, period: TimePeriod) -> str:
        dt = AnalyticsService._ensure_aware(dt)
        if period == TimePeriod.DAILY:
            return dt.strftime("%Y-%m-%d")
        if period == TimePeriod.WEEKLY:
            return f"{dt.isocalendar()[0]}-W{dt.isocalendar()[1]:02d}"
        return dt.strftime("%Y-%m")

    @staticmethod
    def _filter_by_period(items: list, period: TimePeriod, attr: str = "created_at") -> list:
        since = AnalyticsService._since(period)
        filtered = []
        for item in items:
            ts = AnalyticsService._ensure_aware(getattr(item, attr))
            if ts >= since:
                filtered.append(item)
        return filtered

    @staticmethod
    def _trend_from_items(items: list, period: TimePeriod) -> list[TrendPoint]:
        labels = AnalyticsService._bucket_labels(period)
        counts: dict[str, int] = defaultdict(int)
        for item in items:
            key = AnalyticsService._bucket_key(item.created_at, period)
            counts[key] += 1
        return [TrendPoint(label=label, count=counts.get(label, 0)) for label in labels]

    @staticmethod
    def get_analytics(db: Session, period: TimePeriod) -> AnalyticsResponse:
        incidents = AnalyticsService._filter_by_period(db.query(Incident).all(), period)
        tickets = AnalyticsService._filter_by_period(db.query(Ticket).all(), period)
        alerts = AnalyticsService._filter_by_period(db.query(Alert).all(), period)

        severity_counts: dict[str, int] = defaultdict(int)
        for inc in incidents:
            severity_counts[inc.severity.value] += 1

        category_counts: dict[str, int] = defaultdict(int)
        for inc in incidents:
            label = ISSUE_LABELS.get(inc.issue_type, inc.issue_type.value)
            category_counts[label] += 1

        top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:8]
        resolved = sum(
            1 for i in incidents
            if i.status in (IncidentStatus.RESOLVED, IncidentStatus.CLOSED)
        )
        unresolved = len(incidents) - resolved

        ticket_status_counts: dict[str, int] = defaultdict(int)
        for t in tickets:
            ticket_status_counts[t.status.value.replace("_", " ").title()] += 1

        return AnalyticsResponse(
            period=period,
            incident_trends=AnalyticsService._trend_from_items(incidents, period),
            severity_distribution=[
                NameValue(name=k, value=v)
                for k, v in sorted(severity_counts.items())
            ],
            top_error_categories=[
                CategoryCount(category=k, count=v) for k, v in top_categories
            ],
            resolved_vs_unresolved=[
                NameValue(name="Resolved", value=resolved),
                NameValue(name="Unresolved", value=unresolved),
            ],
            alert_frequency=AnalyticsService._trend_from_items(alerts, period),
            ticket_status=[
                NameValue(name=k, value=v)
                for k, v in sorted(ticket_status_counts.items())
            ],
            summary={
                "incidents": len(incidents),
                "tickets": len(tickets),
                "alerts": len(alerts),
                "critical": severity_counts.get("Critical", 0),
            },
        )
