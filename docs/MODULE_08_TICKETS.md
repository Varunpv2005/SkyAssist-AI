# Module 8 — Ticket Management System

## Overview

Support ticket lifecycle management with automatic ticket generation from detected incidents and full CRUD operations.

## Folder Structure (Module 8)

```
skyassist-ai/
├── backend/
│   ├── models/ticket.py           # Ticket ORM + enums
│   ├── schemas/ticket.py          # Pydantic DTOs
│   ├── ticket_engine/
│   │   └── service.py             # Auto-generation logic from incidents
│   ├── services/ticket_service.py   # CRUD + stats
│   ├── routes/tickets.py            # API endpoints
│   └── tests/test_tickets.py
├── frontend/
│   └── src/pages/Tickets.tsx      # Ticket management UI
└── docs/MODULE_08_TICKETS.md
```

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/tickets` | Create ticket (manual or linked to incident) | Yes |
| GET | `/api/v1/tickets` | List all tickets | Yes |
| GET | `/api/v1/tickets/stats` | Ticket summary stats | Yes |
| GET | `/api/v1/tickets/{ticket_id}` | Get single ticket (e.g. TKT-1001) | Yes |
| PATCH | `/api/v1/tickets/{ticket_id}` | Update ticket fields/status | Yes |
| DELETE | `/api/v1/tickets/{ticket_id}` | Delete ticket | Yes |

## Ticket Fields

| Field | Type | Description |
|-------|------|-------------|
| `ticket_id` | string | Auto-generated ID (TKT-1001, TKT-1002, …) |
| `issue` | string | Brief issue summary |
| `priority` | enum | Critical, High, Medium, Low |
| `root_cause` | string | Known or suspected root cause |
| `assigned_to` | string | Assigned analyst username |
| `status` | enum | open, in_progress, resolved, closed |
| `incident_id` | FK | Linked incident (optional) |
| `created_at` | datetime | Creation timestamp |

## Auto-Generation

When a log is parsed and incidents are detected, tickets are **automatically created** for each new incident:

1. Log uploaded → parsed
2. Incident engine detects issues → creates INC-* records
3. Ticket engine maps incident → creates TKT-* records

Priority is mapped from incident severity (Critical → Critical, etc.).

## Status Workflow

```
Open → In Progress → Resolved → Closed
```

## Architecture

```
Incident detected
    ↓
ticket_engine/service.py   ← Build ticket draft from incident
    ↓
services/ticket_service.py ← Persist with TKT-* ID
    ↓
routes/tickets.py          ← REST API
    ↓
frontend/Tickets.tsx       ← UI with create, update, delete
```

## Commands

```bash
# Run ticket tests
cd backend
pytest tests/test_tickets.py -v

# All tests (77 total)
pytest tests/ -v
```

## Next Module

**Module 9 — Alert System**: WebSocket real-time notifications for critical incidents and ticket updates.
