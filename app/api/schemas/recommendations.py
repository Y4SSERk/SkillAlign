# app/api/schemas/recommendations.py

"""
Pydantic schemas for recommendations endpoints.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    """Request schema for occupation recommendations."""

    skills: List[str] = Field(
        ...,
        description="List of skill URIs the user possesses",
        min_length=1,
        example=[
            "http://data.europa.eu/esco/skill/00e8c",
            "http://data.europa.eu/esco/skill/01a2b"
        ]
    )
    occupation_groups: Optional[List[str]] = Field(
        None,
        description="Optional list of occupation group URIs to filter results"
    )
    schemes: Optional[List[str]] = Field(
        None,
        description="Optional list of concept scheme URIs to filter results"
    )
    limit: int = Field(
        20,
        description="Maximum number of recommendations to return",
        ge=1,
        le=100
    )


class SkillMatch(BaseModel):
    """Schema for a matched or missing skill."""

    uri: str = Field(..., description="Skill URI")
    label: str = Field(..., description="Skill label/name")
    skill_type: Optional[str] = Field(None, description="Skill type (knowledge/skill)")
    relation_type: str = Field(..., description="Relation type (essential/optional)")


class OccupationRecommendation(BaseModel):
    """Schema for a single occupation recommendation."""

    uri: str = Field(..., description="Occupation URI")
    label: str = Field(..., description="Occupation title/name")
    description: Optional[str] = Field(None, description="Occupation description")
    isco_code: Optional[str] = Field(None, description="ISCO-08 occupation code")
    similarity_score: float = Field(
        ...,
        description="FAISS similarity score (0-1, higher is better)",
        ge=0.0,
        le=1.0
    )
    match_percentage: float = Field(
        ...,
        description="Percentage of required skills the user already has",
        ge=0.0,
        le=100.0
    )
    matched_skills: List[SkillMatch] = Field(
        default_factory=list,
        description="Skills the user has that this occupation requires"
    )
    missing_skills: List[SkillMatch] = Field(
        default_factory=list,
        description="Skills the user needs to acquire for this occupation"
    )
    groups: List[str] = Field(
        default_factory=list,
        description="Occupation group labels"
    )
    schemes: List[str] = Field(
        default_factory=list,
        description="Concept scheme labels (Digital, Green, etc.)"
    )


class RecommendationResponse(BaseModel):
    """Response schema for occupation recommendations."""

    total: int = Field(..., description="Total number of recommendations returned")
    user_skills: List[str] = Field(..., description="Input skill URIs from the request")
    recommendations: List[OccupationRecommendation] = Field(
        ...,
        description="List of recommended occupations with skill-gap analysis"
    )