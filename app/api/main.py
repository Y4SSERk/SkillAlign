# app/api/main.py

"""
SkillAlign API Main Application
Configures FastAPI app with Neo4j lifecycle and auto-router discovery.
"""

from __future__ import annotations

import importlib
from typing import Optional

from fastapi import APIRouter, FastAPI

from app.core.deps import init_neo4j_client, close_neo4j_client
from app.core.settings import get_settings

settings = get_settings()

app = FastAPI(
    title="SkillAlign API",
    version="0.1.0",
    description="ML-powered occupation recommendation system using ESCO taxonomy"
)


@app.on_event("startup")
def on_startup() -> None:
    """Initialize Neo4j client on application startup."""
    init_neo4j_client()


@app.on_event("shutdown")
def on_shutdown() -> None:
    """Close Neo4j client on application shutdown."""
    close_neo4j_client()


def _try_include(module_path: str) -> bool:
    """
    Tries to import `module_path` and include its `router` (APIRouter).
    Returns True if included, False if the module does not exist yet.
    """
    try:
        mod = importlib.import_module(module_path)
    except ModuleNotFoundError:
        return False

    router: Optional[APIRouter] = getattr(mod, "router", None)
    if router is None:
        raise RuntimeError(f"{module_path} exists but does not export `router`")

    app.include_router(router)
    return True


# Health check (fallback if route not implemented)
if not _try_include("app.api.routes.health"):
    fallback_health_router = APIRouter(tags=["health"])

    @fallback_health_router.get("/health")
    def health() -> dict:
        return {"status": "ok", "environment": settings.environment}

    app.include_router(fallback_health_router)

# Auto-discover and include routers
_try_include("app.api.routes.diagnostics")
_try_include("app.api.routes.catalog")
_try_include("app.api.routes.occupations")
_try_include("app.api.routes.skills")
_try_include("app.api.routes.notes")
_try_include("app.api.routes.recommendations")
