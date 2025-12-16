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


# Additional domain models will be added here as we build out features:
# - Occupation
# - Skill
# - OccupationGroup
# - SkillGroup
# - ConceptScheme
# - Note
# etc.
