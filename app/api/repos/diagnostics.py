# app/api/repos/diagnostics.py

from __future__ import annotations

from typing import Any

from app.core.neo4j import Neo4jClient


class DiagnosticsRepo:
    """
    Data access layer for diagnostics endpoints.
    Returns raw data from Neo4j (no business logic).
    """

    def __init__(self, neo4j_client: Neo4jClient) -> None:
        self.neo4j = neo4j_client

    def get_node_counts_by_label(self) -> list[dict[str, Any]]:
        """
        Count nodes grouped by label.

        Returns:
            List of dicts with keys: label, count
        """
        cypher = """
        MATCH (n)
        RETURN labels(n)[0] AS label, count(n) AS count
        ORDER BY count DESC
        """
        return self.neo4j.run_query(cypher)

    def get_relationship_counts_by_type(self) -> list[dict[str, Any]]:
        """
        Count relationships grouped by type.

        Returns:
            List of dicts with keys: type, count
        """
        cypher = """
        MATCH ()-[r]->()
        RETURN type(r) AS type, count(r) AS count
        ORDER BY count DESC
        """
        return self.neo4j.run_query(cypher)
