# Module 3 — Log Upload System

## Overview

Authenticated file upload for security logs. Supports `.log`, `.txt`, and `.csv` files stored in `skyassist-ai/logs/` with metadata tracked in PostgreSQL.

## Folder Structure (Module 3)

```
backend/
├── models/
│   └── log_file.py          # LogFile ORM + LogStatus enum
├── schemas/
│   └── log.py               # Upload/list response schemas
├── services/
│   └── log_service.py       # Validation, storage, listing
├── routes/
│   └── logs.py              # Upload & list endpoints
└── tests/
    └── test_logs.py         # 8 upload/list tests

frontend/src/
├── pages/Logs.tsx           # Drag-and-drop upload + table
└── services/api.ts          # logsApi.upload(), logsApi.list()
```

## API Endpoints

| Method | Endpoint                  | Description              | Auth |
|--------|---------------------------|--------------------------|------|
| POST   | `/api/v1/logs/upload`     | Upload a log file        | Yes  |
| GET    | `/api/v1/logs`            | List uploaded log files  | Yes  |

## LogFile Model

| Field           | Type     | Description                    |
|-----------------|----------|--------------------------------|
| id              | int      | Primary key                    |
| filename        | string   | Original file name             |
| stored_filename | string   | UUID-prefixed name on disk     |
| file_path       | string   | Full path in `logs/`           |
| file_size       | int      | Size in bytes                  |
| file_type       | string   | Extension (log, txt, csv)        |
| status          | enum     | uploaded / processing / parsed / failed |
| uploaded_by     | FK       | User who uploaded              |
| created_at      | datetime | Upload timestamp               |

## Validation Rules

- Allowed extensions: `.log`, `.txt`, `.csv`
- Max file size: 10 MB (configurable via `MAX_UPLOAD_SIZE_MB`)
- Empty files rejected
- JWT authentication required

## Setup Commands

```bash
# Backend
cd backend
.\venv\Scripts\activate
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm run dev
```

Navigate to **Logs** in the sidebar → upload a file.

## API Usage

### Upload

```bash
curl -X POST http://localhost:8000/api/v1/logs/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@proxy_error.log"
```

### List

```bash
curl http://localhost:8000/api/v1/logs \
  -H "Authorization: Bearer <token>"
```

## Test Results

```
15 passed — 7 auth + 8 log upload/list tests
```

## Next Module

**Module 4 — Log Parser**: Extract timestamp, severity, message, and source from uploaded logs into JSON format.
