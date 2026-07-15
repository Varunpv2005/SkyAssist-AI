# 🚀 SkyAssist AI
### AI-Powered Security Troubleshooting & Incident Analysis Platform

> Intelligent incident management platform that combines **FastAPI**, **React**, **PostgreSQL**, and **Ollama (Llama 3.2)** to provide AI-driven root cause analysis, troubleshooting assistance, and remediation recommendations.

---

## 📌 Overview

Modern IT teams receive thousands of alerts every day, making manual investigation slow and inefficient.

**SkyAssist AI** accelerates incident response by combining structured incident management with a locally hosted Large Language Model (Llama 3.2 via Ollama) to generate:

- Root Cause Analysis (RCA)
- AI-powered troubleshooting
- Step-by-step remediation
- Incident tracking
- Real-time monitoring

Unlike cloud-based AI solutions, SkyAssist AI can operate with **local LLM inference**, helping organizations keep sensitive operational data within their own infrastructure.

---

# ✨ Features

## Incident Management
- Incident creation and tracking
- Severity classification
- Incident history
- Status management

## AI Troubleshooting Assistant
- Natural language troubleshooting
- Root cause analysis
- Confidence scoring
- Structured JSON responses
- Rule-based fallback engine

## AI Remediation Engine
- Recommended fixes
- Troubleshooting workflow
- Resolution steps
- Confidence-based suggestions

## Dashboard & Analytics
- Incident statistics
- Alert analytics
- Ticket overview
- Interactive charts

## Authentication
- JWT Authentication
- Role-based authorization
- Protected APIs
- Secure password hashing

## Real-Time Updates
- WebSocket notifications
- Live dashboard refresh
- Instant alert updates

## Deployment
- Docker Compose
- PostgreSQL
- Environment-based configuration
- Production-ready containerization

---

# 🏗 Architecture

> *(Architecture diagram will be added here.)*

```
                React Frontend
                       │
                       ▼
              FastAPI Backend
                       │
     ┌─────────────────┼─────────────────┐
     ▼                 ▼                 ▼
PostgreSQL        WebSockets       Ollama (Llama 3.2)
     │                                  │
     └──────────────► AI Engine ◄────────┘
                       │
                       ▼
              JSON AI Response
                       │
                       ▼
                  React UI
```

---

# ⚙ Technology Stack

| Layer | Technology |
|--------|------------|
| Frontend | React, TypeScript, TailwindCSS, Vite |
| Backend | FastAPI, Python |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Validation | Pydantic |
| Authentication | JWT |
| AI | Ollama + Llama 3.2 |
| HTTP Client | HTTPX |
| Charts | Recharts |
| Real-Time | WebSockets |
| Deployment | Docker Compose |

---

# 📂 Project Structure

```
backend/
    ai_engine/
    routes/
    models/
    database/
    services/

frontend/
    components/
    pages/
    services/
    hooks/

docker/
docs/

docker-compose.yml
README.md
```

---

# 🔄 Request Flow

```
User
   │
   ▼
React Frontend
   │
   ▼
FastAPI API
   │
   ▼
AI Engine
   │
   ▼
Ollama (Llama 3.2)
   │
   ▼
JSON Response
   │
   ▼
Frontend Chat UI
```

---

# 🤖 AI Workflow

1. User submits a troubleshooting question.
2. FastAPI constructs a structured prompt.
3. Prompt is sent to Ollama.
4. Llama 3.2 generates structured JSON.
5. Backend validates and parses the response.
6. Response is stored in history.
7. Frontend displays:
   - Root Cause
   - Explanation
   - Resolution Steps
   - Confidence Score

If Ollama is unavailable, the application automatically switches to a rule-based fallback engine.

---

# 📊 Screenshots

> *(To be added.)*

- Login Page
- Dashboard
- Incidents
- AI Assistant
- AI Remediation
- Alerts

---

# 🎥 Demo

> Demo video coming soon.

---

# 🚀 Getting Started

## Local Setup

```bash
cd backend

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

copy .env.example .env

uvicorn main:app --reload
```

Frontend

```bash
cd frontend

npm install

npm run dev
```

---

## Docker

```bash
docker compose up -d --build
```

---

# 🔐 Security

- JWT Authentication
- Password hashing
- Input validation
- ORM-based SQL injection protection
- Environment variable configuration
- Role-based authorization

---

# 📈 Future Enhancements

- Redis caching
- Advanced analytics
- Email notifications
- Multi-tenant support
- AI model selection
- Kubernetes deployment

---

# 👨‍💻 Author

**Varun Venugopal**

Computer Science Engineering Student

---

# 📄 License

MIT License
