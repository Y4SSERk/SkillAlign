# app/api/routes/health.py

from __future__ import annotations

from fastapi import APIRouter

from app.core.settings import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    """
    Basic readiness endpoint.

    Note: actual Neo4j connectivity checks will move to services/repos once core.neo4j exists.
    """
    settings = get_settings()

    return {
        "status": "ok",
        "environment": settings.environment,
        "neo4j": {
            "uri_configured": bool(settings.neo4j_uri),
            "user_configured": bool(settings.neo4j_user),
            # Don't leak secrets; just indicate whether a password exists
            "password_configured": bool(settings.neo4j_password),
        },
        "faiss": {
            "index_path": str(settings.faiss_index_path),
            "index_present": settings.faiss_index_path.exists(),
        },
    }
