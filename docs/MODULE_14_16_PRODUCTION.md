# Modules 14–16 — Deployment, Monitoring & Production

## Module 14 — Docker Deployment

### Files
- `docker-compose.yml` — PostgreSQL, backend, frontend (nginx), Ollama (profile `ai`)
- `docker/backend.Dockerfile` — Python 3.11 + Uvicorn (2 workers)
- `docker/frontend.Dockerfile` — Multi-stage Node build + nginx
- `docker/nginx.conf` — SPA routing, `/api` and `/ws` proxy
- `docker/.env.example` — Production environment template
- `docker/start.sh` / `docker/start.ps1` — Startup scripts

### Commands

```bash
# Linux/macOS
./docker/start.sh

# Windows
.\docker\start.ps1

# Without Ollama
docker compose up -d --build

# With Ollama AI
docker compose --profile ai up -d --build
docker exec skyassist-ollama ollama pull llama3.2
```

| Service  | URL |
|----------|-----|
| Frontend | http://localhost |
| Backend  | http://localhost:8000 |
| API docs | http://localhost:8000/docs |

---

## Module 15 — Monitoring

### Endpoints
| Endpoint | Description |
|----------|-------------|
| `GET /health` | DB + Ollama status |
| `GET /metrics` | Request count, errors, avg latency, per-endpoint stats |

### Features
- Structured request logging (`skyassist` logger)
- `RequestLoggingMiddleware` — timing, `X-Response-Time-Ms` header
- `SecurityHeadersMiddleware` — XSS, frame, content-type protections
- Global exception handler with production-safe error messages
- Configurable `LOG_LEVEL` and `ENVIRONMENT`

---

## Module 16 — Production Finish

- **Security:** CORS from `CORS_ORIGINS` env, security headers, production error masking
- **UI:** Error boundary, skip-to-content link, `aria-label` on search, `#main-content` landmark
- **Validation:** Existing Pydantic schemas on all API inputs (unchanged)
- **Tests:** `tests/test_monitoring.py` — health, metrics, security headers
