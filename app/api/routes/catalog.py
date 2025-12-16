# app/api/routes/catalog.py

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query

from app.core.deps import Neo4jDep
from app.api.services.catalog import CatalogService
from app.api.schemas.catalog import (
    OccupationAutocompleteResponse,
    SkillAutocompleteResponse,
    OccupationGroupResponse,
    SkillGroupResponse,
    ConceptSchemeResponse,
)

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/occupations", response_model=list[OccupationAutocompleteResponse])
def get_occupations_autocomplete(
    neo4j: Neo4jDep,
    q: Optional[str] = Query(None, description="Search query for occupation label"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
) -> list[OccupationAutocompleteResponse]:
    """
    Autocomplete search for occupations by label.
    Returns a lightweight list of {uri, label} for dropdown/autocomplete UIs.
    """
    service = CatalogService(neo4j)
    occupations = service.search_occupations_autocomplete(q=q, limit=limit)
    
    return [
        OccupationAutocompleteResponse(uri=occ.uri, label=occ.label)
        for occ in occupations
    ]


@router.get("/skills", response_model=list[SkillAutocompleteResponse])
def get_skills_autocomplete(
    neo4j: Neo4jDep,
    q: Optional[str] = Query(None, description="Search query for skill label"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
) -> list[SkillAutocompleteResponse]:
    """
    Autocomplete search for skills by label.
    Returns a lightweight list of {uri, label} for dropdown/autocomplete UIs.
    """
    service = CatalogService(neo4j)
    skills = service.search_skills_autocomplete(q=q, limit=limit)
    
    return [
        SkillAutocompleteResponse(uri=skill.uri, label=skill.label)
        for skill in skills
    ]


@router.get("/occupation-groups", response_model=list[OccupationGroupResponse])
def get_occupation_groups(
    neo4j: Neo4jDep,
    q: Optional[str] = Query(None, description="Search query for group name"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
) -> list[OccupationGroupResponse]:
    """
    Search occupation groups (ISCO groups) by name.
    Returns {uri, code, label} for filter dropdowns.
    """
    service = CatalogService(neo4j)
    groups = service.search_occupation_groups(q=q, limit=limit)
    
    return [
        OccupationGroupResponse(uri=grp.uri, code=grp.code, label=grp.label)
        for grp in groups
    ]


@router.get("/skill-groups", response_model=list[SkillGroupResponse])
def get_skill_groups(
    neo4j: Neo4jDep,
    q: Optional[str] = Query(None, description="Search query for group name"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
) -> list[SkillGroupResponse]:
    """
    Search skill groups by name.
    Returns {uri, label} for filter dropdowns.
    """
    service = CatalogService(neo4j)
    groups = service.search_skill_groups(q=q, limit=limit)
    
    return [
        SkillGroupResponse(uri=grp.uri, label=grp.label)
        for grp in groups
    ]


@router.get("/concept-schemes", response_model=list[ConceptSchemeResponse])
def get_concept_schemes(
    neo4j: Neo4jDep,
) -> list[ConceptSchemeResponse]:
    """
    List all concept schemes (Digital, Green, Research, etc.).
    Returns {uri, label} for filter dropdowns.
    """
    service = CatalogService(neo4j)
    schemes = service.list_concept_schemes()
    
    return [
        ConceptSchemeResponse(uri=scheme.uri, label=scheme.label)
        for scheme in schemes
    ]
