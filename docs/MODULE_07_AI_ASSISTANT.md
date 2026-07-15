# Module 7 — AI Troubleshooting Assistant

## Overview

AI-powered troubleshooting using **Ollama + Llama 3.2** with automatic **fallback mode** when Ollama is offline. Support engineers can ask natural-language questions about logs and incidents.

## Features

- Natural-language questions: "Why did this error occur?", "Suggest a fix", "How can I resolve this?"
- Input: log snippet, incident ID, severity
- Output: root cause, explanation, resolution steps, confidence score
- Query history stored per user
- Ollama health check endpoint

## Folder Structure

```
backend/
├── ai_engine/
│   ├── prompt_templates/
│   │   └── troubleshoot.py    # System + user prompt templates
│   └── service.py             # Ollama client + fallback logic
├── models/
│   └── ai_history.py          # AI query history table
├── services/
│   └── ai_service.py          # Orchestration + incident context
├── routes/
│   └── ai.py                  # API endpoints
└── tests/
    ├── test_ai_engine.py
    └── test_ai.py
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/ai/ask` | Ask troubleshooting question |
| GET | `/api/v1/ai/history` | User's query history |
| GET | `/api/v1/ai/status` | Ollama availability check |

## Request Example

```json
{
  "question": "Why did this error occur?",
  "log_snippet": "2026-06-15 ERROR [auth-service] Login failed",
  "incident_id": "INC-1001",
  "severity": "High"
}
```

## Response Example

```json
{
  "root_cause": "Authentication failure due to invalid credentials",
  "explanation": "The log shows a failed login attempt...",
  "resolution_steps": ["Verify credentials", "Check auth service"],
  "confidence_score": 0.85,
  "source": "ollama"
}
```

## Ollama Setup

```bash
# Install Ollama: https://ollama.com
ollama pull llama3.2
ollama serve
```

Configure in `.env`:
```
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

When Ollama is offline, the system uses rule-based fallback responses automatically.

## Test Results

```
68 passed — 6 AI engine + 5 API + 57 prior modules
```

## Next Module

**Module 8 — Ticket Management System**: Auto-generate tickets from incidents.
