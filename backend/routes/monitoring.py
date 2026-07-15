from fastapi import APIRouter, Depends

from ai_engine.service import AIEngine
from api.dependencies import get_current_user, require_roles
from middleware.monitoring import check_database, get_metrics
from models.user import User, UserRole

router = APIRouter(tags=["Monitoring"])


@router.get("/health")
async def health_check():
    db = check_database()
    ollama = await AIEngine.check_ollama_health()
    status = "healthy" if db["status"] == "healthy" else "degraded"
    return {
        "status": status,
        "service": "skyassist-ai",
        "database": db,
        "ollama": {"available": ollama.get("available", False), "model": ollama.get("model")},
    }


@router.get("/metrics")
def metrics(current_user: User = Depends(require_roles(UserRole.ADMIN))):
    return get_metrics()
