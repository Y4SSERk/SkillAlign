# app/api/services/diagnostics.py

from __future__ import annotations

from app.core.models import NodeCount, RelCount
from app.core.neo4j import Neo4jClient
from app.api.repos.diagnostics import DiagnosticsRepo


class DiagnosticsService:
    """
    Orchestration layer for diagnostics.
    Calls repos and returns core.models dataclasses.
    """

    def __init__(self, neo4j_client: Neo4jClient) -> None:
        self.repo = DiagnosticsRepo(neo4j_client)

    def get_node_counts_by_label(self) -> list[NodeCount]:
        """
        Retrieve node counts grouped by label.

        Returns:
            List of NodeCount domain models
        """
        raw_counts = self.repo.get_node_counts_by_label()
        return [
            NodeCount(label=row["label"], count=row["count"])
            for row in raw_counts
        ]

    def get_relationship_counts_by_type(self) -> list[RelCount]:
        """
        Retrieve relationship counts grouped by type.

        Returns:
            List of RelCount domain models
        """
        raw_counts = self.repo.get_relationship_counts_by_type()
        return [
            RelCount(type=row["type"], count=row["count"])
            for row in raw_counts
        ]
