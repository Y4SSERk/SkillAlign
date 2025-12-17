# app/core/models.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class NodeCount:
    """Represents a count of nodes grouped by label."""

    label: str
    count: int


@dataclass
class RelCount:
    """Represents a count of relationships grouped by type."""

    type: str
    count: int


# --- Catalog domain models ---


@dataclass
class OccupationAutocomplete:
    """Lightweight occupation for autocomplete/dropdown."""

    uri: str
    label: str


@dataclass
class SkillAutocomplete:
    """Lightweight skill for autocomplete/dropdown."""

    uri: str
    label: str


@dataclass
class OccupationGroup:
    """Occupation group (ISCO group) for filter dropdowns."""

    uri: str
    code: str
    label: str


@dataclass
class SkillGroup:
    """Skill group for filter dropdowns."""

    uri: str
    label: str


@dataclass
class ConceptScheme:
    """Concept scheme (Digital, Green, Research, etc.) for filter dropdowns."""

    uri: str
    label: str


# --- Full domain models ---


@dataclass
class Occupation:
    """Full occupation domain model."""

    uri: str
    label: str
    description: Optional[str] = None
    isco_code: Optional[str] = None


@dataclass
class Skill:
    """Full skill domain model."""

    uri: str
    label: str
    description: Optional[str] = None
    skill_type: Optional[str] = None


@dataclass
class SkillInGap:
    """Skill within a skill gap (with relationship type)."""

    uri: str
    label: str
    relation_type: str  # "essential" or "optional"
    skill_type: Optional[str] = None


@dataclass
class SkillGap:
    """Skill gap for a target occupation."""

    occupation_uri: str
    occupation_label: str
    isco_code: Optional[str] = None
    essential_skills: list[SkillInGap] = field(default_factory=list)
    optional_skills: list[SkillInGap] = field(default_factory=list)


# Additional domain models will be added here as we build out features:
# - Note
# - RelatedSkill
# etc.
