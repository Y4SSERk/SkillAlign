# app/api/routes/skills.py

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query

from app.core.deps import Neo4jDep
from app.api.services.skills import SkillsService
from app.api.schemas.skills import SkillSearchResponse

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("", response_model=list[SkillSearchResponse])
def search_skills(
    neo4j: Neo4jDep,
    q: Optional[str] = Query(None, description="Search query for skill label"),
    type: Optional[str] = Query(None, description="Filter by skill type: 'knowledge' or 'skill/competence'"),
    groups: Optional[str] = Query(None, description="Comma-separated SkillGroup URIs"),
    schemes: Optional[str] = Query(None, description="Comma-separated ConceptScheme URIs"),
    relatedTo: Optional[str] = Query(None, description="Skill URI to find related skills"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
) -> list[SkillSearchResponse]:
    """
    Search skills with optional filters.
    
    Filters:
    - q: Text search on skill label
    - type: Filter by skill type ('knowledge' or 'skill/competence')
    - groups: Filter by skill groups
    - schemes: Filter by concept schemes (Digital, Green, etc.)
    - relatedTo: Find skills related to a specific skill URI
    """
    service = SkillsService(neo4j)
    
    # Parse comma-separated filters
    group_uris = [uri.strip() for uri in groups.split(",")] if groups else None
    scheme_uris = [uri.strip() for uri in schemes.split(",")] if schemes else None
    
    skills = service.search_skills(
        q=q,
        skill_type=type,
        group_uris=group_uris,
        scheme_uris=scheme_uris,
        related_to_uri=relatedTo,
        limit=limit,
        offset=offset,
    )
    
    return [
        SkillSearchResponse(
            uri=skill.uri,
            label=skill.label,
            description=skill.description,
            skillType=skill.skill_type,
        )
        for skill in skills
    ]
