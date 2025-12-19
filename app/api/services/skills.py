# app/api/services/skills.py

from __future__ import annotations

from typing import Optional

from app.core.models import Skill
from app.core.neo4j import Neo4jClient
from app.api.repos.skills import SkillsRepo


class SkillsService:
    """
    Orchestration layer for skill endpoints.
    Calls repos and returns core.models dataclasses.
    """

    def __init__(self, neo4j_client: Neo4jClient) -> None:
        self.repo = SkillsRepo(neo4j_client)

    def search_skills(
        self,
        q: Optional[str],
        skill_type: Optional[str],
        group_uris: Optional[list[str]],
        scheme_uris: Optional[list[str]],
        related_to_uri: Optional[str],
        limit: int,
        offset: int,
    ) -> list[Skill]:
        """
        Search skills with optional filters.

        Returns:
            List of Skill domain models
        """
        raw_results = self.repo.search_skills(
            q=q,
            skill_type=skill_type,
            group_uris=group_uris,
            scheme_uris=scheme_uris,
            related_to_uri=related_to_uri,
            limit=limit,
            offset=offset,
        )
        return [
            Skill(
                uri=row["uri"],
                label=row["label"],
                description=row.get("description"),
                skill_type=row.get("skillType"),
            )
            for row in raw_results
        ]
