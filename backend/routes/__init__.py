from routes.ai import router as ai_router
from routes.analysis import router as analysis_router
from routes.auth import router as auth_router
from routes.incidents import router as incidents_router
from routes.logs import router as logs_router

__all__ = ["auth_router", "logs_router", "incidents_router", "analysis_router", "ai_router"]
