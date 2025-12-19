# app/api/services/recommendations.py

"""
Recommendations Service
Business logic for occupation recommendations.
"""

import logging
from typing import List, Optional

from app.core.neo4j import Neo4jClient
from app.api.repos.recommendations import RecommendationsRepo
from app.api.schemas.recommendations import (
    RecommendationRequest,
    RecommendationResponse,
    OccupationRecommendation,
    SkillMatch
)

logger = logging.getLogger(__name__)


class RecommendationsService:
    """Service for generating occupation recommendations."""

    def __init__(self, neo4j_client: Neo4jClient):
        self.repo = RecommendationsRepo(neo4j_client)

    def get_recommendations(
        self,
        request: RecommendationRequest
    ) -> RecommendationResponse:
        """
        Generate occupation recommendations based on user skills.

        Args:
            request: Recommendation request with skills and filters

        Returns:
            RecommendationResponse with recommended occupations

        Raises:
            ValueError: If input validation fails
        """
        # Validate input
        if not request.skills or len(request.skills) == 0:
            raise ValueError("At least one skill URI is required")

        if request.limit <= 0:
            raise ValueError("Limit must be greater than 0")

        if request.limit > 100:
            raise ValueError("Limit cannot exceed 100")

        # Get recommendations from repo
        try:
            recommendations_data = self.repo.get_recommendations(
                skill_uris=request.skills,
                occupation_groups=request.occupation_groups,
                schemes=request.schemes,
                limit=request.limit
            )

            # Transform to Pydantic models
            recommendations = []
            for rec_data in recommendations_data:
                # Build matched skills
                matched_skills = [
                    SkillMatch(
                        uri=skill["uri"],
                        label=skill["label"],
                        skill_type=skill.get("skill_type"),
                        relation_type=skill.get("relation_type") or "essential"  # Default if None
                    )
                    for skill in rec_data.get("matched_skills", [])
                ]

                # Build missing skills
                missing_skills = [
                    SkillMatch(
                        uri=skill["uri"],
                        label=skill["label"],
                        skill_type=skill.get("skill_type"),
                        relation_type=skill.get("relation_type") or "optional"  # Default if None
                    )
                    for skill in rec_data.get("missing_skills", [])
                ]

                # Create recommendation object
                recommendation = OccupationRecommendation(
                    uri=rec_data["uri"],
                    label=rec_data["label"],
                    description=rec_data.get("description"),
                    isco_code=rec_data.get("isco_code"),
                    similarity_score=rec_data["similarity_score"],
                    match_percentage=rec_data.get("match_percentage", 0.0),
                    matched_skills=matched_skills,
                    missing_skills=missing_skills,
                    groups=rec_data.get("groups", []),
                    schemes=rec_data.get("schemes", [])
                )

                recommendations.append(recommendation)

            return RecommendationResponse(
                total=len(recommendations),
                recommendations=recommendations,
                user_skills=request.skills
            )

        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}", exc_info=True)
            raise RuntimeError(f"Failed to generate recommendations: {str(e)}") from e
