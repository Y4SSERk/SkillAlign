# app/api/schemas/catalog.py

from __future__ import annotations

from pydantic import BaseModel, Field


class OccupationAutocompleteResponse(BaseModel):
    """Lightweight occupation for autocomplete/dropdown."""

    uri: str = Field(..., description="Occupation URI")
    label: str = Field(..., description="Occupation preferred label")


class SkillAutocompleteResponse(BaseModel):
    """Lightweight skill for autocomplete/dropdown."""

    uri: str = Field(..., description="Skill URI")
    label: str = Field(..., description="Skill preferred label")


class OccupationGroupResponse(BaseModel):
    """Occupation group (ISCO group) for filter dropdowns."""

    uri: str = Field(..., description="Occupation group URI")
    code: str = Field(..., description="ISCO code")
    label: str = Field(..., description="Occupation group label")


class SkillGroupResponse(BaseModel):
    """Skill group for filter dropdowns."""

    uri: str = Field(..., description="Skill group URI")
    label: str = Field(..., description="Skill group label")


class ConceptSchemeResponse(BaseModel):
    """Concept scheme (Digital, Green, Research, etc.) for filter dropdowns."""

    uri: str = Field(..., description="Concept scheme URI")
    label: str = Field(..., description="Concept scheme label")
