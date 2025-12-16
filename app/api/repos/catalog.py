# app/api/repos/catalog.py

from __future__ import annotations

from typing import Any

from app.core.neo4j import Neo4jClient


class CatalogRepo:
    """
    Data access layer for catalog (autocomplete/dropdown) endpoints.
    Returns raw data from Neo4j.
    """

    def __init__(self, neo4j_client: Neo4jClient) -> None:
        self.neo4j = neo4j_client

    def search_occupations_autocomplete(
        self, q: str | None, limit: int
    ) -> list[dict[str, Any]]:
        """
        Search occupations by label for autocomplete.

        Returns:
            List of dicts with keys: uri, label
        """
        cypher = """
        MATCH (o:Occupation)
        WHERE o.preferredLabel IS NOT NULL
          AND ($q IS NULL OR toLower(o.preferredLabel) CONTAINS toLower($q))
        RETURN o.uri AS uri, o.preferredLabel AS label
        ORDER BY o.preferredLabel
        LIMIT $limit
        """
        return self.neo4j.run_query(cypher, {"q": q, "limit": limit})

    def search_skills_autocomplete(
        self, q: str | None, limit: int
    ) -> list[dict[str, Any]]:
        """
        Search skills by label for autocomplete.

        Returns:
            List of dicts with keys: uri, label
        """
        cypher = """
        MATCH (s:Skill)
        WHERE s.preferredLabel IS NOT NULL
          AND ($q IS NULL OR toLower(s.preferredLabel) CONTAINS toLower($q))
        RETURN s.uri AS uri, s.preferredLabel AS label
        ORDER BY s.preferredLabel
        LIMIT $limit
        """
        return self.neo4j.run_query(cypher, {"q": q, "limit": limit})

    def search_occupation_groups(
        self, q: str | None, limit: int
    ) -> list[dict[str, Any]]:
        """
        Search occupation groups (ISCO groups) by label.

        Returns:
            List of dicts with keys: uri, code, label
        """
        cypher = """
        MATCH (g:OccupationGroup)
        WHERE $q IS NULL OR toLower(g.label) CONTAINS toLower($q)
        RETURN g.uri AS uri, g.label AS label, g.code AS code
        ORDER BY toLower(g.label)
        LIMIT $limit
        """
        return self.neo4j.run_query(cypher, {"q": q, "limit": limit})

    def search_skill_groups(
        self, q: str | None, limit: int
    ) -> list[dict[str, Any]]:
        """
        Search skill groups by label.

        Returns:
            List of dicts with keys: uri, label
        """
        cypher = """
        MATCH (g:SkillGroup)
        WHERE $q IS NULL OR toLower(g.label) CONTAINS toLower($q)
        RETURN g.uri AS uri, g.label AS label
        ORDER BY toLower(g.label)
        LIMIT $limit
        """
        return self.neo4j.run_query(cypher, {"q": q, "limit": limit})

    def list_concept_schemes(self) -> list[dict[str, Any]]:
        """
        List all concept schemes.

        Returns:
            List of dicts with keys: uri, label
        """
        cypher = """
        MATCH (cs:ConceptScheme)
        RETURN cs.uri AS uri, cs.label AS label
        ORDER BY toLower(cs.label)
        """
        return self.neo4j.run_query(cypher)
