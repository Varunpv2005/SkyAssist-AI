from log_parser.service import parse_log_content, entries_to_json


SAMPLE_LOG = """\
2026-06-15 10:00:00 ERROR [auth-service] Login failed for user admin
2026-06-15 10:01:12 WARNING [proxy-gateway] High latency detected
2026-06-15 10:02:30 INFO [auth-service] User session created
2026-06-15 10:03:45 CRITICAL [database] Connection pool exhausted
ERROR: Token validation failed
"""

SAMPLE_CSV = """\
timestamp,severity,message,source
2026-06-15 10:00:00,ERROR,Login failed,auth-service
2026-06-15 10:01:00,WARNING,Slow response,api-gateway
"""


def test_parse_bracketed_format():
    entries = parse_log_content(SAMPLE_LOG, "log", "proxy.log")
    assert len(entries) == 5
    assert entries[0].severity == "ERROR"
    assert entries[0].source == "auth-service"
    assert "Login failed" in entries[0].message
    assert entries[0].timestamp == "2026-06-15 10:00:00"


def test_parse_critical_severity():
    entries = parse_log_content(SAMPLE_LOG, "log")
    critical = [e for e in entries if e.severity == "CRITICAL"]
    assert len(critical) == 1
    assert critical[0].source == "database"


def test_parse_severity_first_format():
    entries = parse_log_content(SAMPLE_LOG, "log")
    last = entries[-1]
    assert last.severity == "ERROR"
    assert "Token validation" in last.message


def test_parse_csv_format():
    entries = parse_log_content(SAMPLE_CSV, "csv")
    assert len(entries) == 2
    assert entries[0].severity == "ERROR"
    assert entries[0].source == "auth-service"
    assert entries[1].severity == "WARNING"


def test_parse_empty_lines_skipped():
    content = "2026-06-15 10:00:00 INFO [svc] OK\n\n\n2026-06-15 10:01:00 ERROR [svc] Fail"
    entries = parse_log_content(content, "log")
    assert len(entries) == 2


def test_entries_to_json():
    entries = parse_log_content("2026-06-15 10:00:00 ERROR [api] Timeout", "log")
    result = entries_to_json(entries)
    assert len(result) == 1
    assert result[0]["severity"] == "ERROR"
    assert result[0]["source"] == "api"
    assert "timestamp" in result[0]
    assert "message" in result[0]


def test_parse_warn_normalized_to_warning():
    content = "2026-06-15 10:00:00 WARN [svc] Disk space low"
    entries = parse_log_content(content, "log")
    assert entries[0].severity == "WARNING"
