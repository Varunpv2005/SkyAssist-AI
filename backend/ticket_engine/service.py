from dataclasses import dataclass

from incident_engine.service import IssueType
from models.incident import Incident
from models.ticket import PRIORITY_FROM_SEVERITY, TicketPriority

ISSUE_LABELS: dict[IssueType, str] = {
    IssueType.AUTH_FAILURE: "Authentication Failure",
    IssueType.TOKEN_EXPIRED: "Expired Token",
    IssueType.API_TIMEOUT: "API Timeout",
    IssueType.DATABASE_CONNECTION_ERROR: "Database Connection Error",
    IssueType.SSL_HANDSHAKE_FAILURE: "SSL Handshake Failure",
    IssueType.EMAIL_DELIVERY_FAILURE: "Email Delivery Failure",
    IssueType.NETWORK_ERROR: "Network Error",
    IssueType.DNS_ERROR: "DNS Resolution Error",
}


@dataclass
class TicketDraft:
    issue: str
    priority: TicketPriority
    root_cause: str


def build_ticket_from_incident(incident: Incident) -> TicketDraft:
    """Build ticket fields from a detected incident."""
    label = ISSUE_LABELS.get(incident.issue_type, incident.issue_type.value.replace("_", " ").title())
    issue = f"{label} — {incident.incident_id}"
    priority = PRIORITY_FROM_SEVERITY.get(incident.severity, TicketPriority.MEDIUM)
    return TicketDraft(issue=issue, priority=priority, root_cause=incident.root_cause)
