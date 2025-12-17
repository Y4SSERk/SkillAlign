# app/api/repos/occupations.py

from __future__ import annotations

from typing import Any, Optional

from app.core.neo4j import Neo4jClient


class OccupationsRepo:
    """
    Data access layer for occupation endpoints.
    Returns raw data from Neo4j.
    """

    def __init__(self, neo4j_client: Neo4jClient) -> None:
        self.neo4j = neo4j_client

    def search_occupations(
        self,
        q: Optional[str],
        group_uris: Optional[list[str]],
        skill_uris: Optional[list[str]],
        scheme_uris: Optional[list[str]],
        limit: int,
        offset: int,
    ) -> list[dict[str, Any]]:
        """
        Search occupations with optional filters.

        Returns:
            List of dicts with keys: uri, label, description, iscoCode
        """
        # Build dynamic query based on which filters are provided
        has_groups = group_uris and len(group_uris) > 0
        has_skills = skill_uris and len(skill_uris) > 0
        has_schemes = scheme_uris and len(scheme_uris) > 0
        
        cypher = """
        MATCH (o:Occupation)
        WHERE ($q IS NULL OR size($q) = 0 OR toLower(o.preferredLabel) CONTAINS toLower($q))
        """
        
        if has_groups:
            cypher += """
        MATCH (o)-[:IN_OCC_GROUP]->(g:OccupationGroup)
        WHERE g.uri IN $groups
            """
        
        if has_skills:
            cypher += """
        MATCH (o)-[:REQUIRES]->(rs:Skill)
        WHERE rs.uri IN $requiredSkills
            """
        
        if has_schemes:
            cypher += """
        MATCH (o)-[:IN_SCHEME]->(cs:ConceptScheme)
        WHERE cs.uri IN $schemes
            """
        
        cypher += """
        RETURN DISTINCT
          o.uri AS uri,
          o.preferredLabel AS label,
          o.description AS description,
          o.iscoCode AS iscoCode
        ORDER BY toLower(o.preferredLabel)
        SKIP $offset
        LIMIT $limit
        """
        
        params = {
            "q": q or "",
            "groups": group_uris or [],
            "requiredSkills": skill_uris or [],
            "schemes": scheme_uris or [],
            "offset": offset,
            "limit": limit,
        }
        
        return self.neo4j.run_query(cypher, params)

    def get_skill_gap(
        self,
        occupation_uri: str,
        essential_only: bool,
        skill_type: Optional[str],
        skill_group_uris: Optional[list[str]],
        scheme_uris: Optional[list[str]],
    ) -> dict[str, Any]:
        """
        Get skill gap (required skills) for an occupation.

        Returns:
            Dict with keys: occupationUri, occupationLabel, requiredSkills (list)
        """
        cypher = """
        MATCH (o:Occupation {uri: $occupationUri})-[r:REQUIRES]->(s:Skill)
        WHERE ($essentialOnly = false OR toLower(coalesce(r.relation, '')) CONTAINS 'essential')
          AND ($skillType IS NULL OR size($skillType) = 0 OR s.skillType = $skillType)
        OPTIONAL MATCH (s)-[:IN_SKILL_GROUP]->(g:SkillGroup)
        WHERE ($skillGroups IS NULL OR size($skillGroups) = 0 OR g.uri IN $skillGroups)
        OPTIONAL MATCH (s)-[:IN_SCHEME]->(cs:ConceptScheme)
        WHERE ($schemes IS NULL OR size($schemes) = 0 OR cs.uri IN $schemes)
        WITH o, r, s,
             [x IN collect(DISTINCT CASE WHEN g IS NULL THEN NULL ELSE {uri: g.uri, label: g.label} END) WHERE x IS NOT NULL] AS skillGroupsCollected,
             [x IN collect(DISTINCT CASE WHEN cs IS NULL THEN NULL ELSE {uri: cs.uri, label: cs.label} END) WHERE x IS NOT NULL] AS schemesCollected
        WHERE (size($skillGroups) = 0 OR size(skillGroupsCollected) > 0)
          AND (size($schemes) = 0 OR size(schemesCollected) > 0)
        RETURN o.uri AS occupationUri,
               o.preferredLabel AS occupationLabel,
               o.iscoCode AS iscoCode,
               collect({
                 skillUri: s.uri,
                 skillLabel: s.preferredLabel,
                 skillType: s.skillType,
                 relationType: coalesce(r.relation, 'optional'),
                 skillGroups: skillGroupsCollected,
                 schemes: schemesCollected
               }) AS requiredSkills
        """
        params = {
            "occupationUri": occupation_uri,
            "essentialOnly": essential_only,
            "skillType": skill_type or "",
            "skillGroups": skill_group_uris if skill_group_uris else [],
            "schemes": scheme_uris if scheme_uris else [],
        }
        results = self.neo4j.run_query(cypher, params)
        return results[0] if results else {}
