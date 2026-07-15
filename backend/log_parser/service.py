import csv
import io
import re
from dataclasses import dataclass
from enum import Enum


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"
    UNKNOWN = "UNKNOWN"


@dataclass
class ParsedLogEntry:
    timestamp: str | None
    severity: str
    message: str
    source: str | None
    line_number: int


SEVERITY_PATTERN = r"(?:CRITICAL|ERROR|WARNING|WARN|INFO|DEBUG)"
SEVERITY_NORMALIZE = {
    "WARN": "WARNING",
    "CRITICAL": "CRITICAL",
    "ERROR": "ERROR",
    "WARNING": "WARNING",
    "INFO": "INFO",
    "DEBUG": "DEBUG",
}

# 2026-06-15 10:00:00 ERROR [auth-service] Login failed
PATTERN_BRACKETED = re.compile(
    rf"^(?P<timestamp>\d{{4}}-\d{{2}}-\d{{2}}[\sT]\d{{2}}:\d{{2}}:\d{{2}}(?:\.\d+)?(?:Z|[+-]\d{{2}}:\d{{2}})?)"
    rf"\s+(?P<severity>{SEVERITY_PATTERN})"
    rf"(?:\s+\[(?P<source>[^\]]+)\])?"
    rf"\s*(?P<message>.+)$",
    re.IGNORECASE,
)

# 2026-06-15T10:00:00 ERROR auth-service: Connection timeout
PATTERN_COLON_SOURCE = re.compile(
    rf"^(?P<timestamp>\d{{4}}-\d{{2}}-\d{{2}}[\sT]\d{{2}}:\d{{2}}:\d{{2}}(?:\.\d+)?(?:Z|[+-]\d{{2}}:\d{{2}})?)"
    rf"\s+(?P<severity>{SEVERITY_PATTERN})"
    rf"\s+(?P<source>[\w.-]+):\s*(?P<message>.+)$",
    re.IGNORECASE,
)

# ERROR: Something went wrong
PATTERN_SEVERITY_FIRST = re.compile(
    rf"^(?P<severity>{SEVERITY_PATTERN}):\s*(?P<message>.+)$",
    re.IGNORECASE,
)

# [2026-06-15 10:00:00] ERROR message here
PATTERN_BRACKETED_TIMESTAMP = re.compile(
    rf"^\[(?P<timestamp>[^\]]+)\]\s+(?P<severity>{SEVERITY_PATTERN})\s+(?P<message>.+)$",
    re.IGNORECASE,
)


def _normalize_severity(raw: str) -> str:
    upper = raw.upper()
    return SEVERITY_NORMALIZE.get(upper, upper)


def _parse_line(line: str, line_number: int, default_source: str | None = None) -> ParsedLogEntry | None:
    stripped = line.strip()
    if not stripped:
        return None

    for pattern in (PATTERN_BRACKETED, PATTERN_COLON_SOURCE, PATTERN_BRACKETED_TIMESTAMP, PATTERN_SEVERITY_FIRST):
        match = pattern.match(stripped)
        if match:
            groups = match.groupdict()
            return ParsedLogEntry(
                timestamp=groups.get("timestamp"),
                severity=_normalize_severity(groups["severity"]),
                message=groups.get("message", stripped).strip(),
                source=groups.get("source") or default_source,
                line_number=line_number,
            )

    severity_match = re.search(rf"\b({SEVERITY_PATTERN})\b", stripped, re.IGNORECASE)
    if severity_match:
        return ParsedLogEntry(
            timestamp=None,
            severity=_normalize_severity(severity_match.group(1)),
            message=stripped,
            source=default_source,
            line_number=line_number,
        )

    return ParsedLogEntry(
        timestamp=None,
        severity=Severity.INFO.value,
        message=stripped,
        source=default_source,
        line_number=line_number,
    )


def _parse_csv_content(content: str) -> list[ParsedLogEntry]:
    entries: list[ParsedLogEntry] = []
    reader = csv.DictReader(io.StringIO(content))
    if not reader.fieldnames:
        return entries

    field_map = {name.lower().strip(): name for name in reader.fieldnames}
    for line_number, row in enumerate(reader, start=2):
        timestamp = row.get(field_map.get("timestamp", ""), "") or None
        severity_raw = row.get(field_map.get("severity", ""), "INFO")
        message = row.get(field_map.get("message", ""), "")
        source = row.get(field_map.get("source", ""), None) or None

        if not message:
            continue

        entries.append(
            ParsedLogEntry(
                timestamp=timestamp,
                severity=_normalize_severity(severity_raw),
                message=message.strip(),
                source=source,
                line_number=line_number,
            )
        )
    return entries


def parse_log_content(content: str, file_type: str, filename: str | None = None) -> list[ParsedLogEntry]:
    default_source = None
    if filename:
        default_source = filename.rsplit(".", 1)[0]

    if file_type == "csv":
        return _parse_csv_content(content)

    entries: list[ParsedLogEntry] = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        entry = _parse_line(line, line_number, default_source)
        if entry:
            entries.append(entry)
    return entries


def entries_to_json(entries: list[ParsedLogEntry]) -> list[dict]:
    return [
        {
            "timestamp": e.timestamp,
            "severity": e.severity,
            "message": e.message,
            "source": e.source,
            "line_number": e.line_number,
        }
        for e in entries
    ]
