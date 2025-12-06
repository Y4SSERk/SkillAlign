# app/api/routers/__init__.py
from .recommendations import router as recommendations_router
from .graph import router as graph_router

__all__ = ["recommendations_router", "graph_router"]
