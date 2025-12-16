# app/api/routes/diagnostics.py

from __future__ import annotations

from fastapi import APIRouter

from app.core.deps import Neo4jDep
from app.api.services.diagnostics import DiagnosticsService
from app.api.schemas.diagnostics import NodesByLabelResponse, RelsByTypeResponse, NodeCountResponse, RelCountResponse


router = APIRouter(prefix="/admin/diagnostics", tags=["diagnostics"])


@router.get("/nodes-by-label", response_model=NodesByLabelResponse)
def get_nodes_by_label(neo4j: Neo4jDep) -> NodesByLabelResponse:
    """
    Returns node counts grouped by label.
    
    Queries Neo4j to count all nodes grouped by their primary label.
    """
    service = DiagnosticsService(neo4j)
    node_counts = service.get_node_counts_by_label()
    
    return NodesByLabelResponse(
        labels=[
            NodeCountResponse(label=nc.label, count=nc.count)
            for nc in node_counts
        ]
    )


@router.get("/rels-by-type", response_model=RelsByTypeResponse)
def get_rels_by_type(neo4j: Neo4jDep) -> RelsByTypeResponse:
    """
    Returns relationship counts grouped by type.
    
    Queries Neo4j to count all relationships grouped by their type.
    """
    service = DiagnosticsService(neo4j)
    rel_counts = service.get_relationship_counts_by_type()
    
    return RelsByTypeResponse(
        types=[
            RelCountResponse(type=rc.type, count=rc.count)
            for rc in rel_counts
        ]
    )
