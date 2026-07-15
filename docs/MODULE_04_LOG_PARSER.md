# Module 4 — Log Parser

## Overview

Rule-based log parser that extracts structured fields from uploaded `.log`, `.txt`, and `.csv` files into JSON format.

## Output Format

```json
{
  "timestamp": "2026-06-15 10:00:00",
  "severity": "ERROR",
  "message": "Login failed for user admin",
  "source": "auth-service",
  "line_number": 1
}
```

## Folder Structure (Module 4)

```
backend/
├── log_parser/
│   └── service.py              # Pure parsing logic (regex + CSV)
├── models/
│   └── log_entry.py            # Parsed entry ORM model
├── schemas/
│   └── log_parser.py           # Parse response schemas
├── services/
│   └── log_parser_service.py   # Orchestration (read file, save entries)
└── tests/
    └── test_log_parser.py      # 7 unit tests

frontend/src/
├── components/logs/ParsedEntriesPanel.tsx
└── pages/Logs.tsx              # Parse + View buttons
```

## Supported Log Formats

| Format | Example |
|--------|---------|
| Bracketed source | `2026-06-15 10:00:00 ERROR [auth-service] Login failed` |
| Colon source | `2026-06-15T10:00:00 ERROR auth-service: Timeout` |
| Bracketed timestamp | `[2026-06-15 10:00:00] WARNING Disk low` |
| Severity-first | `ERROR: Token validation failed` |
| CSV columns | `timestamp,severity,message,source` |

## Severity Levels

`CRITICAL` · `ERROR` · `WARNING` · `INFO` · `DEBUG`

## API Endpoints

| Method | Endpoint                       | Description              |
|--------|--------------------------------|--------------------------|
| POST   | `/api/v1/logs/{id}/parse`      | Parse a log file         |
| GET    | `/api/v1/logs/{id}/entries`    | Get parsed entries       |

## Architecture

```
POST /logs/{id}/parse
    ↓
routes/logs.py
    ↓
services/log_parser_service.py   ← DB orchestration, status updates
    ↓
log_parser/service.py            ← Pure regex/CSV parsing (no DB)
    ↓
models/log_entry.py              ← Store entries, update LogFile status
```

## Test Results

```
27 passed — 7 parser unit + 5 parse API + 15 prior modules
```

## Next Module

**Module 5 — Incident Engine**: Rule-based detection for AUTH_FAILURE, API_TIMEOUT, etc.
