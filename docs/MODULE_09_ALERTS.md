# Module 9 — Alert System

## Overview

Real-time alert notifications via WebSockets for critical incidents, ticket updates, and new alerts. Includes toast notifications and a live activity feed on the dashboard.

## Folder Structure (Module 9)

```
skyassist-ai/
├── backend/
│   ├── models/alert.py            # Alert ORM model
│   ├── schemas/alert.py           # Pydantic DTOs
│   ├── websocket/
│   │   └── manager.py             # ConnectionManager for broadcast
│   ├── services/alert_service.py  # Create, list, broadcast alerts
│   ├── routes/ws.py               # WebSocket /ws endpoint
│   ├── routes/alerts.py           # REST alert API
│   └── tests/test_alerts.py, test_websocket.py
├── frontend/
│   ├── src/context/AlertContext.tsx
│   ├── src/components/alerts/
│   │   ├── ToastContainer.tsx
│   │   └── AlertDropdown.tsx
│   └── vite.config.ts             # /ws proxy for dev
└── docs/MODULE_09_ALERTS.md
```

## WebSocket Endpoint

```
ws://localhost:8000/ws?token=<JWT_ACCESS_TOKEN>
```

- JWT required via query parameter
- Broadcasts `{"event": "alert", "alert": {...}}` payloads
- Auto-reconnects on disconnect (frontend, 3s interval)

## REST Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/alerts` | List recent alerts |
| GET | `/api/v1/alerts/stats` | Alert statistics |
| PATCH | `/api/v1/alerts/{alert_id}/read` | Mark single alert read |
| POST | `/api/v1/alerts/read-all` | Mark all alerts read |

## Alert Triggers

| Event | Alert Type | Severity |
|-------|------------|----------|
| Incident detected on log parse | `incident` | Mapped from incident level |
| Auto-ticket created | `ticket` | Mapped from ticket priority |
| Manual ticket created | `ticket` | Mapped from priority |
| Ticket status updated | `ticket` | Mapped from priority |

Critical incidents get a `Critical:` prefix in the alert title.

## Frontend Features

- **Toast notifications** — top-right, auto-dismiss after 5s
- **Navbar bell** — unread count badge + dropdown list
- **Live dashboard** — Recent Activity updates in real time
- **Connection indicator** — green dot when WebSocket is connected

## Architecture

```
Incident/Ticket event
    ↓
AlertService.create_*_alert()  → PostgreSQL
    ↓
AlertService.broadcast()       → ConnectionManager
    ↓
/ws WebSocket clients          → AlertContext
    ↓
Toast + Dashboard activity feed
```

## Commands

```bash
# Run alert tests
pytest tests/test_alerts.py tests/test_websocket.py -v

# All tests (86 total)
pytest tests/ -v
```

## Next Module

**Module 10 — Analytics Dashboard**: Recharts visualizations with daily/weekly/monthly filters.
