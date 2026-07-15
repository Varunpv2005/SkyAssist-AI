from incident_engine.service import detect_from_entry, detect_from_entries, IssueType


def test_detect_auth_failure():
    result = detect_from_entry("Login failed for user admin", "auth-service", 1, "ERROR")
    assert result is not None
    assert result.issue_type == IssueType.AUTH_FAILURE
    assert result.severity.value == "High"


def test_detect_token_expired():
    result = detect_from_entry("JWT token expired for session abc123", "auth-service", 2)
    assert result is not None
    assert result.issue_type == IssueType.TOKEN_EXPIRED


def test_detect_api_timeout():
    result = detect_from_entry("API timeout on /api/v1/proxy after 30s", "gateway", 3)
    assert result is not None
    assert result.issue_type == IssueType.API_TIMEOUT


def test_detect_database_error():
    result = detect_from_entry("Connection pool exhausted on primary database", "database", 4, "CRITICAL")
    assert result is not None
    assert result.issue_type == IssueType.DATABASE_CONNECTION_ERROR
    assert result.severity.value == "Critical"


def test_detect_ssl_failure():
    result = detect_from_entry("SSL handshake failure with gateway.skyhigh.local", "proxy", 5)
    assert result is not None
    assert result.issue_type == IssueType.SSL_HANDSHAKE_FAILURE


def test_detect_dns_error():
    result = detect_from_entry("DNS resolution failed for api.internal", "dns", 6)
    assert result is not None
    assert result.issue_type == IssueType.DNS_ERROR


def test_detect_no_match():
    result = detect_from_entry("User session created successfully", "auth-service", 7)
    assert result is None


def test_detect_deduplicates_by_type_and_source():
    entries = [
        {"id": 1, "message": "Login failed", "source": "auth-service", "severity": "ERROR"},
        {"id": 2, "message": "Authentication failed again", "source": "auth-service", "severity": "ERROR"},
        {"id": 3, "message": "API timeout on endpoint", "source": "gateway", "severity": "ERROR"},
    ]
    results = detect_from_entries(entries)
    assert len(results) == 2
    types = {r.issue_type for r in results}
    assert IssueType.AUTH_FAILURE in types
    assert IssueType.API_TIMEOUT in types
