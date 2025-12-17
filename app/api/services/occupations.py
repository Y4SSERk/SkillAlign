# app/api/services/occupations.py

from __future__ import annotations

from typing import Optional

from app.core.models import Occupation, SkillGap, SkillInGap
from app.core.neo4j import Neo4jClient
from app.api.repos.occupations import OccupationsRepo
from app.api.schemas.occupations import SkillGapResponse, SkillInGapResponse


class OccupationsService:
    """
    Orchestration layer for occupation endpoints.
    Calls repos and returns core.models dataclasses.
    """

    def __init__(self, neo4j_client: Neo4jClient) -> None:
        self.repo = OccupationsRepo(neo4j_client)

    def search_occupations(
        self,
        q: Optional[str],
        group_uris: Optional[list[str]],
        skill_uris: Optional[list[str]],
        scheme_uris: Optional[list[str]],
        limit: int,
        offset: int,
    ) -> list[Occupation]:
        """
        Search occupations with optional filters.

        Returns:
            List of Occupation domain models
        """
        raw_results = self.repo.search_occupations(
            q=q,
            group_uris=group_uris,
            skill_uris=skill_uris,
            scheme_uris=scheme_uris,
            limit=limit,
            offset=offset,
        )
        return [
            Occupation(
                uri=row["uri"],
                label=row["label"],
                description=row.get("description"),
                isco_code=row.get("iscoCode"),
            )
            for row in raw_results
        ]

    def get_skill_gap(
        self,
        occupation_uri: str,
        essential_only: bool,
        skill_type: Optional[str],
        skill_group_uris: Optional[list[str]],
        scheme_uris: Optional[list[str]],
    ) -> SkillGapResponse:
        """
        Get skill gap for a target occupation.

        Returns:
            SkillGapResponse Pydantic model (for direct route response)
        """
        raw_result = self.repo.get_skill_gap(
            occupation_uri=occupation_uri,
            essential_only=essential_only,
            skill_type=skill_type,
            skill_group_uris=skill_group_uris,
            scheme_uris=scheme_uris,
        )

        if not raw_result:
            # Occupation not found - return empty response
            return SkillGapResponse(
                occupationUri=occupation_uri,
                occupationLabel="Unknown",
                iscoCode=None,
                essentialSkills=[],
                optionalSkills=[],
            )

        # Parse skills and split into essential/optional
        essential_skills = []
        optional_skills = []

        for skill in raw_result.get("requiredSkills", []):
            if not skill.get("skillUri"):  # Skip null skills
                continue

            relation_type = skill.get("relationType", "optional")
            
            skill_response = SkillInGapResponse(
                uri=skill["skillUri"],
                label=skill.get("skillLabel", ""),
                relationType=relation_type,
                skillType=skill.get("skillType"),
            )

            if "essential" in relation_type.lower():
                essential_skills.append(skill_response)
            else:
                optional_skills.append(skill_response)

        return SkillGapResponse(
            occupationUri=raw_result["occupationUri"],
            occupationLabel=raw_result["occupationLabel"],
            iscoCode=raw_result.get("iscoCode"),
            essentialSkills=essential_skills,
            optionalSkills=optional_skills,
        )
