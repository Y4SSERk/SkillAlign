from typing import List
from pydantic import BaseModel, Field


class SkillInput(BaseModel):
    """Input payload for recommendations."""
    skills: List[str] = Field(
        ...,
        description="List of user skills as plain text.",
    )
    top_k: int = Field(
        10,
        ge=1,
        le=50,
        description="Number of recommendations to return.",
    )


class RecommendationItem(BaseModel):
    """Single recommended occupation."""
    occupation_uri: str = Field(
        ...,
        description="URI or ID of the recommended occupation.",
    )
    occupation_label: str = Field(
        ...,
        description="Human-readable label/title of the occupation.",
    )
    score: float = Field(
        ...,
        description="Relevance score (higher = better).",
    )


class RecommendationResponse(BaseModel):
    """Response wrapper for recommendations endpoint."""
    recommendations: List[RecommendationItem]
