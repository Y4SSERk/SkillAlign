# app/api/services/catalog.py

from __future__ import annotations

from app.core.models import (
    OccupationAutocomplete,
    SkillAutocomplete,
    OccupationGroup,
    SkillGroup,
    ConceptScheme,
)
from app.core.neo4j import Neo4jClient
from app.api.repos.catalog import CatalogRepo


class CatalogService:
    """
    Orchestration layer for catalog (autocomplete/dropdown) endpoints.
    Calls repos and returns core.models dataclasses.
    """

    def __init__(self, neo4j_client: Neo4jClient) -> None:
        self.repo = CatalogRepo(neo4j_client)

    def search_occupations_autocomplete(
        self, q: str | None, limit: int
    ) -> list[OccupationAutocomplete]:
        """
        Search occupations for autocomplete.

        Args:
            q: Search query (optional)
            limit: Maximum number of results

        Returns:
            List of OccupationAutocomplete domain models
        """
        raw_results = self.repo.search_occupations_autocomplete(q=q, limit=limit)
        return [
            OccupationAutocomplete(uri=row["uri"], label=row["label"])
            for row in raw_results
        ]

    def search_skills_autocomplete(
        self, q: str | None, limit: int
    ) -> list[SkillAutocomplete]:
        """
        Search skills for autocomplete.

        Args:
            q: Search query (optional)
            limit: Maximum number of results

        Returns:
            List of SkillAutocomplete domain models
        """
        raw_results = self.repo.search_skills_autocomplete(q=q, limit=limit)
        return [
            SkillAutocomplete(uri=row["uri"], label=row["label"])
            for row in raw_results
        ]

    def search_occupation_groups(
        self, q: str | None, limit: int
    ) -> list[OccupationGroup]:
        """
        Search occupation groups (ISCO groups).

        Args:
            q: Search query (optional)
            limit: Maximum number of results

        Returns:
            List of OccupationGroup domain models
        """
        raw_results = self.repo.search_occupation_groups(q=q, limit=limit)
        return [
            OccupationGroup(uri=row["uri"], code=row["code"], label=row["label"])
            for row in raw_results
        ]

    def search_skill_groups(
        self, q: str | None, limit: int
    ) -> list[SkillGroup]:
        """
        Search skill groups.

        Args:
            q: Search query (optional)
            limit: Maximum number of results

        Returns:
            List of SkillGroup domain models
        """
        raw_results = self.repo.search_skill_groups(q=q, limit=limit)
        return [
            SkillGroup(uri=row["uri"], label=row["label"])
            for row in raw_results
        ]

    def list_concept_schemes(self) -> list[ConceptScheme]:
        """
        List all concept schemes.

        Returns:
            List of ConceptScheme domain models
        """
        raw_results = self.repo.list_concept_schemes()
        return [
            ConceptScheme(uri=row["uri"], label=row["label"])
            for row in raw_results
        ]
