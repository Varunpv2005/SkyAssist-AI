# Module 6 — Root Cause Analysis Engine

## Overview

Rule-based root cause analysis that takes detected incidents and produces structured findings with possible causes, recommended actions, and confidence scores. No AI — pure deterministic rules.

## Output Format

```json
{
  "issue": "Authentication Failure",
  "possible_causes": [
    "Invalid username or password submitted",
    "Account locked due to repeated failed attempts",
    "Authentication service unavailable or degraded"
  ],
  "recommended_action": "Verify user credentials, check account lockout status...",
  "confidence_score": 0.88
}
```

## Confidence Scoring

| Factor | Boost |
|--------|-------|
| Base score per issue type | 0.77 – 0.91 |
| Critical severity | +0.08 |
| High severity | +0.05 |
| Source identified | +0.03 |
| Keyword match in description | +0.02 – 0.05 |
| Maximum cap | 0.99 |

## Supported Issues

| Issue | Base Confidence |
|-------|----------------|
| Database Connection Failure | 0.91 |
| Expired Security Token | 0.88 |
| SSL/TLS Certificate Problem | 0.86 |
| DNS Resolution Failure | 0.84 |
| Authentication Failure | 0.82 |
| Network Connectivity Failure | 0.80 |
| API Timeout | 0.79 |
| SMTP / Email Delivery Failure | 0.77 |

## Folder Structure

```
backend/
├── rca_engine/
│   └── service.py           # Pure RCA rules + confidence scoring
├── models/
│   └── rca.py               # RootCauseAnalysis ORM model
├── services/
│   └── rca_service.py       # DB orchestration
├── routes/
│   └── analysis.py          # API endpoints
└── tests/
    ├── test_rca_engine.py
    └── test_analysis.py
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/analysis/incident/{id}` | Run RCA on incident |
| GET | `/api/v1/analysis/incident/{id}` | Get RCA result |
| GET | `/api/v1/analysis` | List all analyses |

## Architecture

```
Incident (from Module 5)
    ↓
routes/analysis.py
    ↓
services/rca_service.py      ← Persist results
    ↓
rca_engine/service.py        ← Rule-based analysis (no DB)
    ↓
models/rca.py                ← Store RCA with confidence score
```

## Test Results

```
57 passed — 9 RCA unit + 6 API + 42 prior modules
```

## Next Module

**Module 7 — AI Troubleshooting Assistant**: Ollama + Llama 3.2 for AI-powered analysis.
