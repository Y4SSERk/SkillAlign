# app/api/schemas/occupations.py

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class OccupationSearchResponse(BaseModel):
    """Response model for a single occupation in search results."""

    uri: str = Field(..., description="Occupation URI")
    label: str = Field(..., description="Occupation preferred label")
    description: Optional[str] = Field(None, description="Occupation description")
    iscoCode: Optional[str] = Field(None, description="ISCO occupation code")


class SkillInGapResponse(BaseModel):
    """Response model for a skill within a skill gap."""

    uri: str = Field(..., description="Skill URI")
    label: str = Field(..., description="Skill preferred label")
    relationType: str = Field(..., description="Relationship type (essential/optional)")
    skillType: Optional[str] = Field(None, description="Skill type (skill/competence or knowledge)")


class SkillGapResponse(BaseModel):
    """Response model for GET /occupations/{occupationUri}/skill-gap"""

    occupationUri: str = Field(..., description="Target occupation URI")
    occupationLabel: str = Field(..., description="Target occupation label")
    iscoCode: Optional[str] = Field(None, description="ISCO code")
    essentialSkills: list[SkillInGapResponse] = Field(default_factory=list, description="Essential skills")
    optionalSkills: list[SkillInGapResponse] = Field(default_factory=list, description="Optional skills")
