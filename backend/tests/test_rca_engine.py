from incident_engine.service import IncidentLevel, IssueType
from rca_engine.service import analyze


def test_analyze_auth_failure():
    result = analyze(
        IssueType.AUTH_FAILURE,
        IncidentLevel.HIGH,
        "Login failed for user admin from 192.168.1.1",
        "auth-service",
    )
    assert result.issue == "Authentication Failure"
    assert len(result.possible_causes) >= 3
    assert result.confidence_score >= 0.82
    assert result.confidence_score <= 0.99


def test_analyze_database_critical_boost():
    result = analyze(
        IssueType.DATABASE_CONNECTION_ERROR,
        IncidentLevel.CRITICAL,
        "Connection pool exhausted on primary database",
        "database",
    )
    assert result.issue == "Database Connection Failure"
    assert result.confidence_score >= 0.91


def test_analyze_api_timeout():
    result = analyze(
        IssueType.API_TIMEOUT,
        IncidentLevel.HIGH,
        "API timeout on /api/v1/proxy after 30s",
        "gateway",
    )
    assert result.issue == "API Timeout"
    assert "upstream" in result.recommended_action.lower() or "timeout" in result.recommended_action.lower()


def test_analyze_ssl_certificate():
    result = analyze(
        IssueType.SSL_HANDSHAKE_FAILURE,
        IncidentLevel.HIGH,
        "SSL certificate expired on gateway.skyhigh.local",
        "proxy",
    )
    assert result.issue == "SSL/TLS Certificate Problem"
    assert result.confidence_score >= 0.86


def test_analyze_token_expired():
    result = analyze(
        IssueType.TOKEN_EXPIRED,
        IncidentLevel.MEDIUM,
        "JWT token expired for session",
        "auth-service",
    )
    assert result.issue == "Expired Security Token"


def test_analyze_dns_error():
    result = analyze(
        IssueType.DNS_ERROR,
        IncidentLevel.MEDIUM,
        "DNS resolution failed for api.internal",
        "dns",
    )
    assert result.issue == "DNS Resolution Failure"


def test_analyze_network_error():
    result = analyze(
        IssueType.NETWORK_ERROR,
        IncidentLevel.HIGH,
        "Connection refused to upstream host",
        "network",
    )
    assert result.issue == "Network Connectivity Failure"


def test_analyze_email_failure():
    result = analyze(
        IssueType.EMAIL_DELIVERY_FAILURE,
        IncidentLevel.MEDIUM,
        "SMTP error sending alert notification",
        "mail",
    )
    assert result.issue == "SMTP / Email Delivery Failure"


def test_confidence_capped_at_99():
    result = analyze(
        IssueType.DATABASE_CONNECTION_ERROR,
        IncidentLevel.CRITICAL,
        "Connection pool exhausted connection refused",
        "database",
    )
    assert result.confidence_score <= 0.99
