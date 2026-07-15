import logging
import time
from collections import defaultdict
from datetime import datetime, timezone

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy import text
from starlette.middleware.base import BaseHTTPMiddleware

from database.config import settings
from database.session import engine

logger = logging.getLogger("skyassist")

_metrics = {
    "request_count": 0,
    "error_count": 0,
    "total_duration_ms": 0.0,
    "by_endpoint": defaultdict(int),
    "by_status": defaultdict(int),
    "started_at": datetime.now(timezone.utc).isoformat(),
}


def get_metrics() -> dict:
    count = _metrics["request_count"]
    avg_ms = (_metrics["total_duration_ms"] / count) if count else 0
    return {
        "request_count": count,
        "error_count": _metrics["error_count"],
        "avg_duration_ms": round(avg_ms, 2),
        "by_endpoint": dict(_metrics["by_endpoint"]),
        "by_status": dict(_metrics["by_status"]),
        "started_at": _metrics["started_at"],
        "environment": settings.ENVIRONMENT,
    }


def check_database() -> dict:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception as exc:
        return {"status": "unhealthy", "detail": str(exc)}


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        path = request.url.path
        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start) * 1000
            _metrics["request_count"] += 1
            _metrics["total_duration_ms"] += duration_ms
            _metrics["by_endpoint"][path] += 1
            _metrics["by_status"][str(response.status_code)] += 1
            if response.status_code >= 500:
                _metrics["error_count"] += 1
            logger.info(
                "%s %s %s %.1fms",
                request.method,
                path,
                response.status_code,
                duration_ms,
            )
            response.headers["X-Response-Time-Ms"] = f"{duration_ms:.1f}"
            return response
        except Exception:
            _metrics["error_count"] += 1
            _metrics["request_count"] += 1
            logger.exception("Unhandled error on %s %s", request.method, path)
            raise


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        if settings.ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("API error: %s %s", request.method, request.url.path)
    detail = "Internal server error" if settings.ENVIRONMENT == "production" else str(exc)
    return JSONResponse(status_code=500, content={"detail": detail})
