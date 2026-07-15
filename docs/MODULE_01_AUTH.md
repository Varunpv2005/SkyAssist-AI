# Module 1 — User Authentication

## Overview

JWT-based authentication with role-based access control (RBAC) for three roles:
**Admin**, **Analyst**, and **User**.

## Folder Structure (Module 1)

```
skyassist-ai/
├── backend/
│   ├── api/
│   │   └── dependencies.py      # JWT dependency injection, role guards
│   ├── database/
│   │   ├── config.py            # Environment settings (Pydantic Settings)
│   │   └── session.py           # SQLAlchemy engine & session factory
│   ├── models/
│   │   └── user.py              # User ORM model + UserRole enum
│   ├── schemas/
│   │   └── auth.py              # Pydantic request/response schemas
│   ├── services/
│   │   └── auth_service.py      # Business logic (hash, JWT, register, login)
│   ├── routes/
│   │   └── auth.py              # API route handlers
│   ├── tests/
│   │   ├── conftest.py          # Test fixtures (SQLite in-memory)
│   │   └── test_auth.py         # Auth endpoint tests
│   ├── main.py                  # FastAPI application entry point
│   ├── requirements.txt
│   └── .env.example
├── logs/
├── frontend/                    # (Module 2+)
├── docker/                      # (Module 14)
└── docs/
```

## API Endpoints

| Method | Endpoint              | Description                    | Auth Required |
|--------|-----------------------|--------------------------------|---------------|
| POST   | `/api/v1/auth/register` | Register new user            | No            |
| POST   | `/api/v1/auth/login`    | Login, returns JWT           | No            |
| GET    | `/api/v1/auth/me`       | Get current user profile     | Yes (Bearer)  |
| GET    | `/health`               | Health check                 | No            |

## User Roles

| Role     | Value      | Typical Use Case              |
|----------|------------|-------------------------------|
| Admin    | `admin`    | Full platform administration  |
| Analyst  | `analyst`  | Security incident investigation |
| User     | `user`     | Default read/submit access    |

## Architecture Layers

```
Request → routes/auth.py → services/auth_service.py → models/user.py → PostgreSQL
                ↓
         schemas/auth.py (validation)
                ↓
         api/dependencies.py (JWT verification)
```

## Setup Commands

```bash
# 1. Navigate to backend
cd skyassist-ai/backend

# 2. Create virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux

# 5. Start PostgreSQL (or use Docker in Module 14)
# Update DATABASE_URL in .env

# 6. Run the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 7. Run tests
pytest tests/ -v
```

## API Usage Examples

### Register

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "analyst1",
    "email": "analyst@skyhigh.com",
    "password": "securepass123",
    "role": "analyst"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "analyst1", "password": "securepass123"}'
```

### Get Profile

```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <your_access_token>"
```

## Interactive Docs

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Security Best Practices Applied

- Passwords hashed with **bcrypt** (never stored in plain text)
- JWT tokens with configurable expiration
- Role embedded in token payload for downstream authorization
- Pydantic validation on all inputs (email format, password length)
- `require_roles()` dependency for future protected endpoints
- CORS configured for frontend origins

## Next Module

**Module 2 — Dashboard**: React frontend with sidebar, navbar, dark mode, and KPI cards.
