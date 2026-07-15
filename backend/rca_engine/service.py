from dataclasses import dataclass

from incident_engine.service import IncidentLevel, IssueType


@dataclass
class RCARule:
    issue_type: IssueType
    issue: str
    possible_causes: list[str]
    recommended_action: str
    base_confidence: float


@dataclass
class RCAResult:
    issue: str
    possible_causes: list[str]
    recommended_action: str
    confidence_score: float


RCA_RULES: dict[IssueType, RCARule] = {
    IssueType.AUTH_FAILURE: RCARule(
        issue_type=IssueType.AUTH_FAILURE,
        issue="Authentication Failure",
        possible_causes=[
            "Invalid username or password submitted",
            "Account locked due to repeated failed attempts",
            "Authentication service unavailable or degraded",
            "Misconfigured SSO or LDAP integration",
            "Expired or revoked user credentials",
        ],
        recommended_action=(
            "Verify user credentials, check account lockout status, "
            "review auth service health, and inspect recent configuration changes to identity providers."
        ),
        base_confidence=0.82,
    ),
    IssueType.TOKEN_EXPIRED: RCARule(
        issue_type=IssueType.TOKEN_EXPIRED,
        issue="Expired Security Token",
        possible_causes=[
            "JWT or session token exceeded TTL",
            "Client clock skew causing premature expiration",
            "Token refresh mechanism not functioning",
            "Session invalidated server-side",
        ],
        recommended_action=(
            "Refresh the authentication token, verify token TTL settings, "
            "check NTP synchronization, and validate refresh token flow."
        ),
        base_confidence=0.88,
    ),
    IssueType.API_TIMEOUT: RCARule(
        issue_type=IssueType.API_TIMEOUT,
        issue="API Timeout",
        possible_causes=[
            "Upstream service responding slowly or unresponsive",
            "Network latency between gateway and backend",
            "Timeout threshold configured too aggressively",
            "Backend resource exhaustion (CPU/memory)",
            "Database query taking too long",
        ],
        recommended_action=(
            "Check upstream service health and response times, review timeout "
            "configurations, scale backend resources, and optimize slow database queries."
        ),
        base_confidence=0.79,
    ),
    IssueType.DATABASE_CONNECTION_ERROR: RCARule(
        issue_type=IssueType.DATABASE_CONNECTION_ERROR,
        issue="Database Connection Failure",
        possible_causes=[
            "Database server is down or unreachable",
            "Connection pool exhausted",
            "Invalid database credentials or permissions",
            "Network firewall blocking database port",
            "Maximum connection limit reached on DB server",
        ],
        recommended_action=(
            "Verify database server status, increase connection pool size, "
            "check credentials and firewall rules, and review active connection count."
        ),
        base_confidence=0.91,
    ),
    IssueType.SSL_HANDSHAKE_FAILURE: RCARule(
        issue_type=IssueType.SSL_HANDSHAKE_FAILURE,
        issue="SSL/TLS Certificate Problem",
        possible_causes=[
            "SSL certificate has expired",
            "Certificate chain is incomplete or invalid",
            "Hostname mismatch on certificate",
            "TLS version incompatibility between client and server",
            "Self-signed certificate not trusted",
        ],
        recommended_action=(
            "Renew expired certificates, verify the full certificate chain, "
            "check TLS configuration, and ensure hostname matches the certificate CN/SAN."
        ),
        base_confidence=0.86,
    ),
    IssueType.EMAIL_DELIVERY_FAILURE: RCARule(
        issue_type=IssueType.EMAIL_DELIVERY_FAILURE,
        issue="SMTP / Email Delivery Failure",
        possible_causes=[
            "SMTP server is down or rejecting connections",
            "Sender IP blocked or on spam blacklist",
            "Invalid recipient address or mailbox full",
            "Authentication failure with mail server",
            "Email rate limit exceeded",
        ],
        recommended_action=(
            "Check SMTP server status, verify sender reputation, "
            "validate recipient addresses, and review mail server authentication settings."
        ),
        base_confidence=0.77,
    ),
    IssueType.NETWORK_ERROR: RCARule(
        issue_type=IssueType.NETWORK_ERROR,
        issue="Network Connectivity Failure",
        possible_causes=[
            "Target host is unreachable",
            "Firewall or security group blocking traffic",
            "Network route misconfiguration",
            "Load balancer health check failing",
            "Packet loss or high network latency",
        ],
        recommended_action=(
            "Verify network routes and firewall rules, check target host availability, "
            "test connectivity with traceroute/ping, and review load balancer configuration."
        ),
        base_confidence=0.80,
    ),
    IssueType.DNS_ERROR: RCARule(
        issue_type=IssueType.DNS_ERROR,
        issue="DNS Resolution Failure",
        possible_causes=[
            "DNS server is unreachable",
            "Hostname does not exist (NXDOMAIN)",
            "Stale DNS cache entry",
            "Misconfigured DNS records",
            "DNS propagation delay after record change",
        ],
        recommended_action=(
            "Verify DNS server configuration, flush DNS cache, "
            "check DNS records for the hostname, and allow time for propagation if recently changed."
        ),
        base_confidence=0.84,
    ),
}

SEVERITY_BOOST = {
    IncidentLevel.CRITICAL: 0.08,
    IncidentLevel.HIGH: 0.05,
    IncidentLevel.MEDIUM: 0.02,
    IncidentLevel.LOW: 0.0,
}

KEYWORD_BOOSTERS: dict[IssueType, list[tuple[str, float]]] = {
    IssueType.AUTH_FAILURE: [
        ("lockout", 0.04),
        ("brute", 0.05),
        ("invalid credential", 0.03),
    ],
    IssueType.DATABASE_CONNECTION_ERROR: [
        ("pool exhaust", 0.05),
        ("connection refused", 0.04),
        ("refused", 0.03),
    ],
    IssueType.API_TIMEOUT: [
        ("504", 0.04),
        ("gateway", 0.03),
        ("30s", 0.02),
    ],
    IssueType.SSL_HANDSHAKE_FAILURE: [
        ("expir", 0.05),
        ("certificate", 0.03),
    ],
}


def _calculate_confidence(
    rule: RCARule,
    severity: IncidentLevel,
    description: str,
    source: str | None,
) -> float:
    score = rule.base_confidence
    score += SEVERITY_BOOST.get(severity, 0)

    if source:
        score += 0.03

    desc_lower = description.lower()
    for keyword, boost in KEYWORD_BOOSTERS.get(rule.issue_type, []):
        if keyword in desc_lower:
            score += boost

    return round(min(score, 0.99), 2)


def analyze(
    issue_type: IssueType,
    severity: IncidentLevel,
    description: str,
    source: str | None = None,
) -> RCAResult:
    rule = RCA_RULES.get(issue_type)
    if not rule:
        return RCAResult(
            issue="Unknown Issue",
            possible_causes=["Insufficient data to determine root cause"],
            recommended_action="Collect additional log data and re-run analysis.",
            confidence_score=0.50,
        )

    return RCAResult(
        issue=rule.issue,
        possible_causes=rule.possible_causes,
        recommended_action=rule.recommended_action,
        confidence_score=_calculate_confidence(rule, severity, description, source),
    )
