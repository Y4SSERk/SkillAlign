# app/api/schemas/diagnostics.py

from __future__ import annotations

from pydantic import BaseModel, Field


class NodeCountResponse(BaseModel):
    """Response model for a single node label count."""

    label: str = Field(..., description="Node label")
    count: int = Field(..., ge=0, description="Number of nodes with this label")


class NodesByLabelResponse(BaseModel):
    """Response model for GET /admin/diagnostics/nodes-by-label"""

    labels: list[NodeCountResponse] = Field(..., description="Node counts by label")


class RelCountResponse(BaseModel):
    """Response model for a single relationship type count."""

    type: str = Field(..., description="Relationship type")
    count: int = Field(..., ge=0, description="Number of relationships of this type")


class RelsByTypeResponse(BaseModel):
    """Response model for GET /admin/diagnostics/rels-by-type"""

    types: list[RelCountResponse] = Field(..., description="Relationship counts by type")
