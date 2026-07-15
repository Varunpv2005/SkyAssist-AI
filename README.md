# SKYASSIST AI

**AI-Powered Security Troubleshooting and Incident Analysis Platform**

## Status

All 16 modules complete.

## Tech Stack

- **Frontend:** React, TypeScript, TailwindCSS, Recharts
- **Backend:** Python, FastAPI, SQLAlchemy, Pydantic, JWT
- **Database:** PostgreSQL
- **AI:** Ollama + Llama 3.2
- **Real-time:** WebSockets
- **Deployment:** Docker Compose

## Quick Start (Local)

```bash
# Backend
cd backend && python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt && copy .env.example .env
uvicorn main:app --reload

# Frontend
cd frontend && npm install && npm run dev
```

## Docker Deployment

```bash
# From project root
.\docker\start.ps1          # Windows
./docker/start.sh           # Linux/macOS

# Or manually
cp docker/.env.example docker/.env
docker compose --profile ai up -d --build
```

| URL | Service |
|-----|---------|
| http://localhost | Frontend |
| http://localhost:8000/docs | API |
| http://localhost:8000/health | Health |
| http://localhost:8000/metrics | Metrics |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT signing key |
| `CORS_ORIGINS` | Comma-separated allowed origins |
| `ENVIRONMENT` | `development` or `production` |
| `LOG_LEVEL` | `DEBUG`, `INFO`, `WARNING` |
| `OLLAMA_BASE_URL` | Ollama API URL |

See `backend/.env.example` and `docker/.env.example`.

## Documentation

- [Modules 1–10](docs/)
- [Modules 14–16 — Deployment & Production](docs/MODULE_14_16_PRODUCTION.md)

## License

MIT — Portfolio / Educational Project
