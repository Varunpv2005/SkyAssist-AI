import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.config import settings
from database.session import Base, engine
from middleware.monitoring import (
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
    global_exception_handler,
)
from routes.ai import router as ai_router
from routes.alerts import router as alerts_router
from routes.analysis import router as analysis_router
from routes.analytics import router as analytics_router
from routes.auth import router as auth_router
from routes.incidents import router as incidents_router
from routes.knowledge import router as knowledge_router
from routes.logs import router as logs_router
from routes.monitoring import router as monitoring_router
from routes.search import router as search_router
from routes.tickets import router as tickets_router
from routes.ws import router as ws_router


def _configure_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    _configure_logging()
    if settings.ENVIRONMENT != "production":
        Base.metadata.create_all(bind=engine)
    else:
        logging.getLogger("skyassist").info(
            "Skipping create_all in production; use Alembic migrations"
        )
    logging.getLogger("skyassist").info("SKYASSIST AI started [%s]", settings.ENVIRONMENT)
    yield


app = FastAPI(
    title="SKYASSIST AI",
    description="AI-Powered Security Troubleshooting and Incident Analysis Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_exception_handler(Exception, global_exception_handler)

origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)

app.include_router(monitoring_router)
app.include_router(auth_router, prefix="/api/v1")
app.include_router(logs_router, prefix="/api/v1")
app.include_router(incidents_router, prefix="/api/v1")
app.include_router(analysis_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")
app.include_router(tickets_router, prefix="/api/v1")
app.include_router(alerts_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")
app.include_router(knowledge_router, prefix="/api/v1")
app.include_router(ws_router)
