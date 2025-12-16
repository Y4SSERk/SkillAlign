# app/core/models.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


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


# Additional domain models will be added here as we build out features:
# - Occupation (full)
# - Skill (full)
# - Note
# etc.
