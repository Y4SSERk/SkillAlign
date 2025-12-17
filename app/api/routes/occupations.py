# app/api/routes/occupations.py

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query, Path

from app.core.deps import Neo4jDep
from app.api.services.occupations import OccupationsService
from app.api.schemas.occupations import (
    OccupationSearchResponse,
    SkillGapResponse,
)

router = APIRouter(prefix="/occupations", tags=["occupations"])


@router.get("", response_model=list[OccupationSearchResponse])
def search_occupations(
    neo4j: Neo4jDep,
    q: Optional[str] = Query(None, description="Search query for occupation label"),
    groups: Optional[str] = Query(None, description="Comma-separated OccupationGroup URIs"),
    requiredSkills: Optional[str] = Query(None, description="Comma-separated Skill URIs"),
    schemes: Optional[str] = Query(None, description="Comma-separated ConceptScheme URIs"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
) -> list[OccupationSearchResponse]:
    """
    Search occupations with optional filters.
    
    Filters:
    - q: Text search on occupation label
    - groups: Filter by occupation groups (ISCO)
    - requiredSkills: Filter by required skills
    - schemes: Filter by concept schemes (Digital, Green, etc.)
    """
    service = OccupationsService(neo4j)
    
    # Parse comma-separated filters
    group_uris = [uri.strip() for uri in groups.split(",")] if groups else None
    skill_uris = [uri.strip() for uri in requiredSkills.split(",")] if requiredSkills else None
    scheme_uris = [uri.strip() for uri in schemes.split(",")] if schemes else None
    
    occupations = service.search_occupations(
        q=q,
        group_uris=group_uris,
        skill_uris=skill_uris,
        scheme_uris=scheme_uris,
        limit=limit,
        offset=offset,
    )
    
    return [
        OccupationSearchResponse(
            uri=occ.uri,
            label=occ.label,
            description=occ.description,
            iscoCode=occ.isco_code,
        )
        for occ in occupations
    ]


@router.get("/{occupationUri:path}/skill-gap", response_model=SkillGapResponse)
def get_skill_gap(
    neo4j: Neo4jDep,
    occupationUri: str = Path(..., description="Occupation URI (URL-encoded)"),
    essentialOnly: bool = Query(False, description="Return only essential skills"),
    skillType: Optional[str] = Query(None, description="Filter by skill type: 'knowledge' or 'skill/competence'"),
    skillGroups: Optional[str] = Query(None, description="Comma-separated SkillGroup URIs"),
    schemes: Optional[str] = Query(None, description="Comma-separated ConceptScheme URIs"),
) -> SkillGapResponse:
    """
    Get skill gap (required skills) for a target occupation.
    
    Returns essential and optional skills, optionally filtered by:
    - essentialOnly: Show only essential skills
    - skillType: Filter by 'knowledge' or 'skill/competence'
    - skillGroups: Filter by skill groups
    - schemes: Filter by concept schemes
    """
    service = OccupationsService(neo4j)
    
    # Parse comma-separated filters
    skill_group_uris = [uri.strip() for uri in skillGroups.split(",")] if skillGroups else None
    scheme_uris = [uri.strip() for uri in schemes.split(",")] if schemes else None
    
    skill_gap = service.get_skill_gap(
        occupation_uri=occupationUri,
        essential_only=essentialOnly,
        skill_type=skillType,
        skill_group_uris=skill_group_uris,
        scheme_uris=scheme_uris,
    )
    
    return skill_gap
