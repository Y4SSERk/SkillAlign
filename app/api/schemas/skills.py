# app/api/schemas/skills.py

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class SkillSearchResponse(BaseModel):
    """Response model for a single skill in search results."""

    uri: str = Field(..., description="Skill URI")
    label: str = Field(..., description="Skill preferred label")
    description: Optional[str] = Field(None, description="Skill description")
    skillType: Optional[str] = Field(None, description="Skill type (skill/competence or knowledge)")
