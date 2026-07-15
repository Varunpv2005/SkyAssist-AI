# Module 10 — Analytics Dashboard

## Overview

Recharts-powered analytics dashboard with aggregated metrics from incidents, tickets, and alerts. Supports Daily, Weekly, and Monthly time filters.

## Folder Structure (Module 10)

```
skyassist-ai/
├── backend/
│   ├── schemas/analytics.py       # Analytics response DTOs
│   ├── services/analytics_service.py  # Aggregation logic
│   ├── routes/analytics.py        # GET /analytics
│   └── tests/test_analytics.py
├── frontend/
│   ├── src/pages/Analytics.tsx    # Charts + period filter
│   └── package.json               # recharts dependency
└── docs/MODULE_10_ANALYTICS.md
```

## API Endpoint

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/analytics?period=daily` | Aggregated chart data |

**Period values:** `daily` (7 days), `weekly` (8 weeks), `monthly` (6 months)

## Charts

| Chart | Type | Data Source |
|-------|------|-------------|
| Incident Trends | Line | Incidents over time |
| Severity Distribution | Pie | Critical / High / Medium / Low |
| Top Error Categories | Horizontal Bar | Issue types (AUTH_FAILURE, etc.) |
| Resolved vs Unresolved | Bar | Incident status breakdown |
| Alert Frequency | Line | Alerts over time |
| Ticket Status | Pie | Open / In Progress / Resolved / Closed |

## Response Shape

```json
{
  "period": "daily",
  "incident_trends": [{"label": "2026-07-02", "count": 3}],
  "severity_distribution": [{"name": "Critical", "value": 1}],
  "top_error_categories": [{"category": "Auth Failure", "count": 2}],
  "resolved_vs_unresolved": [{"name": "Resolved", "value": 0}, {"name": "Unresolved", "value": 3}],
  "alert_frequency": [{"label": "2026-07-02", "count": 5}],
  "ticket_status": [{"name": "Open", "value": 2}],
  "summary": {"incidents": 3, "tickets": 2, "alerts": 5, "critical": 1}
}
```

## Commands

```bash
# Run analytics tests
pytest tests/test_analytics.py -v

# All tests (91 total)
pytest tests/ -v
```

## Next Module

**Module 11 — Search and Filtering**: Search incidents, tickets, and logs by ID, severity, source, and date.
