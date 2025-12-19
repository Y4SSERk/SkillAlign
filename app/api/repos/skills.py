# app/api/repos/skills.py

from __future__ import annotations

from typing import Any, Optional

from app.core.neo4j import Neo4jClient


class SkillsRepo:
    """
    Data access layer for skill endpoints.
    Returns raw data from Neo4j.
    """

    def __init__(self, neo4j_client: Neo4jClient) -> None:
        self.neo4j = neo4j_client

    def search_skills(
        self,
        q: Optional[str],
        skill_type: Optional[str],
        group_uris: Optional[list[str]],
        scheme_uris: Optional[list[str]],
        related_to_uri: Optional[str],
        limit: int,
        offset: int,
    ) -> list[dict[str, Any]]:
        """
        Search skills with optional filters.

        Returns:
            List of dicts with keys: uri, label, description, skillType
        """
        # Convert empty strings to None for proper NULL checking
        search_query = q if q and q.strip() else None
        skill_type_filter = skill_type if skill_type and skill_type.strip() else None
        
        has_groups = group_uris and len(group_uris) > 0
        has_schemes = scheme_uris and len(scheme_uris) > 0
        
        # Base MATCH based on whether we are searching related skills or all skills
        if related_to_uri:
            cypher = """
            MATCH (s:Skill {uri: $relatedToUri})-[:RELATED_SKILL]-(related:Skill)
            WITH related AS s
            WHERE ($q IS NULL OR size($q) = 0 OR toLower(s.preferredLabel) CONTAINS toLower($q))
              AND ($skillType IS NULL OR size($skillType) = 0 OR s.skillType = $skillType)
            """
        else:
            cypher = """
            MATCH (s:Skill)
            WHERE ($q IS NULL OR size($q) = 0 OR toLower(s.preferredLabel) CONTAINS toLower($q))
              AND ($skillType IS NULL OR size($skillType) = 0 OR s.skillType = $skillType)
            """
            
        if has_groups:
            cypher += """
            MATCH (s)-[:IN_SKILL_GROUP]->(g:SkillGroup)
            WHERE g.uri IN $groups
            """
            
        if has_schemes:
            cypher += """
            MATCH (s)-[:IN_SCHEME]->(cs:ConceptScheme)
            WHERE cs.uri IN $schemes
            """
            
        cypher += """
        RETURN DISTINCT
          s.uri AS uri,
          s.preferredLabel AS label,
          s.description AS description,
          s.skillType AS skillType
        ORDER BY toLower(s.preferredLabel)
        SKIP $offset
        LIMIT $limit
        """
        
        params = {
            "q": search_query or "",
            "skillType": skill_type_filter or "",
            "relatedToUri": related_to_uri,
            "groups": group_uris or [],
            "schemes": scheme_uris or [],
            "offset": offset,
            "limit": limit,
        }
        
        return self.neo4j.run_query(cypher, params)
