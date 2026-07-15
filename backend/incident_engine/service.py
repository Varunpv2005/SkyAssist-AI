import enum
import re
from dataclasses import dataclass


class IssueType(str, enum.Enum):
    AUTH_FAILURE = "AUTH_FAILURE"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    API_TIMEOUT = "API_TIMEOUT"
    DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"
    SSL_HANDSHAKE_FAILURE = "SSL_HANDSHAKE_FAILURE"
    EMAIL_DELIVERY_FAILURE = "EMAIL_DELIVERY_FAILURE"
    NETWORK_ERROR = "NETWORK_ERROR"
    DNS_ERROR = "DNS_ERROR"


class IncidentLevel(str, enum.Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


@dataclass
class DetectionRule:
    issue_type: IssueType
    patterns: list[str]
    severity: IncidentLevel
    root_cause: str
    description_template: str
    recommendation: str


@dataclass
class DetectedIncident:
    issue_type: IssueType
    severity: IncidentLevel
    root_cause: str
    description: str
    recommendation: str
    source: str | None
    log_entry_id: int | None
    matched_line: str


DETECTION_RULES: list[DetectionRule] = [
    DetectionRule(
        issue_type=IssueType.AUTH_FAILURE,
        patterns=[
            r"auth.*fail",
            r"login\s+fail",
            r"authentication\s+fail",
            r"invalid\s+credential",
            r"unauthorized\s+access",
            r"access\s+denied",
        ],
        severity=IncidentLevel.HIGH,
        root_cause="Authentication or authorization failure",
        description_template="Authentication failure detected: {message}",
        recommendation="Verify credentials, check auth service logs, review failed login attempts and lockout policies.",
    ),
    DetectionRule(
        issue_type=IssueType.TOKEN_EXPIRED,
        patterns=[
            r"token\s+expir",
            r"jwt\s+expir",
            r"session\s+expir",
            r"bearer\s+token\s+invalid",
        ],
        severity=IncidentLevel.MEDIUM,
        root_cause="Expired or invalid security token",
        description_template="Token expiration detected: {message}",
        recommendation="Refresh the authentication token, verify token TTL settings, and check clock synchronization.",
    ),
    DetectionRule(
        issue_type=IssueType.API_TIMEOUT,
        patterns=[
            r"api\s+timeout",
            r"request\s+timeout",
            r"gateway\s+timeout",
            r"timed?\s+out",
            r"504\s+gateway",
        ],
        severity=IncidentLevel.HIGH,
        root_cause="API endpoint timeout",
        description_template="API timeout detected: {message}",
        recommendation="Check upstream service health, increase timeout thresholds, and review network latency.",
    ),
    DetectionRule(
        issue_type=IssueType.DATABASE_CONNECTION_ERROR,
        patterns=[
            r"database.*connection",
            r"db\s+connection\s+fail",
            r"connection\s+pool\s+exhaust",
            r"sql.*error",
            r"postgres.*refused",
            r"mysql.*gone\s+away",
        ],
        severity=IncidentLevel.CRITICAL,
        root_cause="Database connectivity failure",
        description_template="Database connection error: {message}",
        recommendation="Verify database server status, check connection pool settings, and review firewall rules.",
    ),
    DetectionRule(
        issue_type=IssueType.SSL_HANDSHAKE_FAILURE,
        patterns=[
            r"ssl\s+handshake",
            r"certificate\s+expir",
            r"tls\s+error",
            r"cert(ificate)?\s+invalid",
            r"ssl.*fail",
        ],
        severity=IncidentLevel.HIGH,
        root_cause="SSL/TLS certificate or handshake failure",
        description_template="SSL/TLS issue detected: {message}",
        recommendation="Renew certificates, verify certificate chain, and check TLS configuration on endpoints.",
    ),
    DetectionRule(
        issue_type=IssueType.EMAIL_DELIVERY_FAILURE,
        patterns=[
            r"email\s+deliver.*fail",
            r"smtp\s+error",
            r"mail\s+send\s+fail",
            r"bounce",
            r"550\s+",
        ],
        severity=IncidentLevel.MEDIUM,
        root_cause="Email delivery failure",
        description_template="Email delivery failure: {message}",
        recommendation="Check SMTP server status, verify sender reputation, and review email queue.",
    ),
    DetectionRule(
        issue_type=IssueType.NETWORK_ERROR,
        patterns=[
            r"network\s+error",
            r"connection\s+refused",
            r"connection\s+reset",
            r"host\s+unreachable",
            r"no\s+route\s+to\s+host",
        ],
        severity=IncidentLevel.HIGH,
        root_cause="Network connectivity failure",
        description_template="Network error detected: {message}",
        recommendation="Check network routes, firewall rules, and upstream service availability.",
    ),
    DetectionRule(
        issue_type=IssueType.DNS_ERROR,
        patterns=[
            r"dns\s+error",
            r"dns\s+resolution\s+fail",
            r"name\s+resolution\s+fail",
            r"unknown\s+host",
            r"nxdomain",
        ],
        severity=IncidentLevel.MEDIUM,
        root_cause="DNS resolution failure",
        description_template="DNS resolution error: {message}",
        recommendation="Verify DNS server configuration, check DNS cache, and validate hostname records.",
    ),
]


def _match_rule(message: str, rule: DetectionRule) -> bool:
    text = message.lower()
    return any(re.search(pattern, text) for pattern in rule.patterns)


def detect_from_entry(
    message: str,
    source: str | None,
    log_entry_id: int | None,
    severity: str | None = None,
) -> DetectedIncident | None:
    for rule in DETECTION_RULES:
        if _match_rule(message, rule):
            adjusted_severity = rule.severity
            if severity and severity.upper() == "CRITICAL" and rule.severity != IncidentLevel.CRITICAL:
                adjusted_severity = IncidentLevel.CRITICAL

            return DetectedIncident(
                issue_type=rule.issue_type,
                severity=adjusted_severity,
                root_cause=rule.root_cause,
                description=rule.description_template.format(message=message[:200]),
                recommendation=rule.recommendation,
                source=source,
                log_entry_id=log_entry_id,
                matched_line=message,
            )
    return None


def detect_from_entries(entries: list[dict]) -> list[DetectedIncident]:
    incidents: list[DetectedIncident] = []
    seen_types: set[str] = set()

    for entry in entries:
        message = entry.get("message", "")
        source = entry.get("source")
        log_entry_id = entry.get("id")
        severity = entry.get("severity")

        detected = detect_from_entry(message, source, log_entry_id, severity)
        if detected:
            key = f"{detected.issue_type.value}:{source or 'unknown'}"
            if key not in seen_types:
                seen_types.add(key)
                incidents.append(detected)

    return incidents
