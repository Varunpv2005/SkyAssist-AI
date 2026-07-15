# Module 5 — Incident Engine

## Overview

Rule-based incident detection that analyzes parsed log entries and automatically creates structured security incidents with severity, root cause, and recommendations.

## Detection Rules

| Issue Type | Severity | Trigger Patterns |
|------------|----------|------------------|
| `AUTH_FAILURE` | High | login failed, auth fail, unauthorized |
| `TOKEN_EXPIRED` | Medium | token expired, jwt expired, session expired |
| `API_TIMEOUT` | High | api timeout, request timeout, 504 gateway |
| `DATABASE_CONNECTION_ERROR` | Critical | connection pool, db connection fail |
| `SSL_HANDSHAKE_FAILURE` | High | ssl handshake, certificate expired |
| `EMAIL_DELIVERY_FAILURE` | Medium | smtp error, email delivery fail |
| `NETWORK_ERROR` | High | connection refused, network error |
| `DNS_ERROR` | Medium | dns resolution fail, unknown host |

## Incident Fields

Each incident includes:

- **Incident ID** — `INC-1001`, `INC-1002`, ...
- **Severity** — Critical, High, Medium, Low
- **Root Cause** — Rule-defined cause description
- **Description** — Context from matched log line
- **Recommendation** — Suggested remediation steps
- **Status** — open, investigating, resolved, closed

## Folder Structure

```
backend/
├── incident_engine/
│   └── service.py           # Pure detection rules (no DB)
├── models/
│   └── incident.py          # Incident ORM model
├── services/
│   └── incident_service.py  # DB orchestration + ID generation
├── routes/
│   └── incidents.py         # API endpoints
└── tests/
    ├── test_incident_engine.py
    └── test_incidents.py
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/incidents/detect/{log_id}` | Run detection on parsed log |
| GET | `/api/v1/incidents` | List all incidents |
| GET | `/api/v1/incidents/stats` | Summary statistics |
| GET | `/api/v1/incidents/{id}` | Get incident (e.g. INC-1001) |
| PATCH | `/api/v1/incidents/{id}` | Update status |

## Auto-Detection Flow

```
Upload log → Parse log → Auto-detect incidents → Display on Incidents page
```

Incidents are automatically created when a log file is parsed.

## Test Results

```
42 passed — 8 engine unit + 7 incident API + 27 prior modules
```

## Next Module

**Module 6 — Root Cause Analysis Engine**: Deeper analysis with confidence scores and recommended actions.
