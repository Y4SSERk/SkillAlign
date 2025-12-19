# app/api/repos/recommendations.py

"""
Recommendations Repository
Handles FAISS search and Neo4j queries for occupation recommendations.
"""

import logging
from typing import List, Optional, Dict, Any

from app.core.ml import ml_engine
from app.core.neo4j import Neo4jClient

logger = logging.getLogger(__name__)


class RecommendationsRepo:
    """Repository for recommendation queries combining FAISS and Neo4j."""

    def __init__(self, neo4j_client: Neo4jClient):
        self.neo4j_client = neo4j_client

    def get_recommendations(
        self,
        skill_uris: List[str],
        occupation_groups: Optional[List[str]] = None,
        schemes: Optional[List[str]] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get occupation recommendations based on user skills.

        Args:
            skill_uris: List of skill URIs the user possesses
            occupation_groups: Optional list of occupation group URIs to filter by
            schemes: Optional list of concept scheme URIs to filter by
            limit: Maximum number of recommendations to return

        Returns:
            List of occupation dicts with matched/missing skills and similarity scores
        """
        if not skill_uris:
            return []

        # Step 1: Get skill labels from Neo4j
        skill_labels = self._get_skill_labels(skill_uris)

        # Step 2: Create embedding from skill labels
        combined_text = " ".join(skill_labels)
        query_embedding = ml_engine.encode([combined_text])[0]

        # Step 3: Search FAISS for candidate occupations
        faiss_limit = limit * 3 if (occupation_groups or schemes) else limit
        faiss_results = ml_engine.search(query_embedding, top_k=faiss_limit)

        if not faiss_results:
            return []

        candidate_uris = [uri for uri, _ in faiss_results]
        scores_map = {uri: score for uri, score in faiss_results}

        # Step 4: Fetch occupations with skills from Neo4j
        occupations = self._fetch_occupations_with_skills(
            occupation_uris=candidate_uris,
            user_skill_uris=skill_uris,
            occupation_groups=occupation_groups,
            schemes=schemes
        )

        # Step 5: Compute skill-gap analysis and add similarity scores
        enriched = []
        for occ in occupations:
            uri = occ["uri"]
            occ["similarity_score"] = scores_map.get(uri, 0.0)
            
            # Compute matched and missing skills
            required_skill_uris = {s["uri"] for s in occ.get("required_skills", [])}
            user_skill_set = set(skill_uris)
            
            matched_uris = required_skill_uris & user_skill_set
            missing_uris = required_skill_uris - user_skill_set
            
            occ["matched_skills"] = [
                s for s in occ.get("required_skills", []) if s["uri"] in matched_uris
            ]
            occ["missing_skills"] = [
                s for s in occ.get("required_skills", []) if s["uri"] in missing_uris
            ]
            occ["match_percentage"] = (
                len(matched_uris) / len(required_skill_uris) * 100
                if required_skill_uris else 0.0
            )
            
            enriched.append(occ)

        # Step 6: Sort by similarity score and limit
        enriched.sort(key=lambda x: x["similarity_score"], reverse=True)
        return enriched[:limit]

    def _get_skill_labels(self, skill_uris: List[str]) -> List[str]:
        """
        Fetch skill labels from Neo4j given skill URIs.

        Args:
            skill_uris: List of skill URIs

        Returns:
            List of skill labels (preserves order)
        """
        query = """
        MATCH (s:Skill)
        WHERE s.uri IN $uris
        RETURN s.uri AS uri, s.preferredLabel AS label
        """
        
        results = self.neo4j_client.run_query(query, {"uris": skill_uris})
        
        # Create a mapping and preserve order
        label_map = {rec["uri"]: rec["label"] for rec in results}
        labels = [label_map.get(uri, uri) for uri in skill_uris]
        
        return labels

    def _fetch_occupations_with_skills(
        self,
        occupation_uris: List[str],
        user_skill_uris: List[str],
        occupation_groups: Optional[List[str]] = None,
        schemes: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch occupation details and required skills from Neo4j with optional filters.

        Args:
            occupation_uris: List of candidate occupation URIs from FAISS
            user_skill_uris: User's skill URIs for gap analysis
            occupation_groups: Optional occupation group URIs to filter by
            schemes: Optional concept scheme URIs to filter by

        Returns:
            List of occupation dicts with required skills
        """
        query = """
        MATCH (o:Occupation)
        WHERE o.uri IN $occupation_uris
        """
        
        # Add occupation group filter WITH hierarchical support
        if occupation_groups:
            # Extract codes from URIs for pattern matching
            group_codes = [uri.split('/C')[-1] for uri in occupation_groups]
            
            query += """
            AND (
                EXISTS {
                    MATCH (o)-[:IN_OCC_GROUP]->(g:OccupationGroup)
                    WHERE g.uri IN $occupation_groups
                }
                OR EXISTS {
                    MATCH (o)-[:IN_OCC_GROUP]->(g:OccupationGroup)-[:broaderTransitive|broader*1..5]->(parent:OccupationGroup)
                    WHERE parent.uri IN $occupation_groups
                }
                OR EXISTS {
                    MATCH (o)-[:IN_OCC_GROUP]->(g:OccupationGroup)
                    WHERE ANY(code IN $occupation_group_codes WHERE g.code STARTS WITH code)
                }
            )
            """
        
        # Add scheme filter
        if schemes:
            query += """
            AND EXISTS {
                MATCH (o)-[:IN_SCHEME]->(cs:ConceptScheme)
                WHERE cs.uri IN $schemes
            }
            """
        
        query += """
        // Fetch required skills
        OPTIONAL MATCH (o)-[r:REQUIRES]->(s:Skill)
        
        // Fetch occupation groups (handle null labels)
        OPTIONAL MATCH (o)-[:IN_OCC_GROUP]->(g:OccupationGroup)
        
        // Fetch schemes (handle null labels)
        OPTIONAL MATCH (o)-[:IN_SCHEME]->(cs:ConceptScheme)
        
        WITH o, 
             COLLECT(DISTINCT {
                 uri: s.uri, 
                 label: s.preferredLabel,
                 relation_type: r.relationType,
                 skill_type: s.skillType
             }) AS required_skills,
             COLLECT(DISTINCT COALESCE(g.preferredLabel, g.code, g.uri)) AS groups,
             COLLECT(DISTINCT COALESCE(cs.preferredLabel, cs.uri)) AS schemes
        
        RETURN o.uri AS uri,
               o.preferredLabel AS label,
               o.description AS description,
               o.iscoCode AS isco_code,
               required_skills,
               groups,
               schemes
        ORDER BY o.preferredLabel
        """
        
        params = {
            "occupation_uris": occupation_uris,
            "user_skill_uris": user_skill_uris
        }
        
        if occupation_groups:
            params["occupation_groups"] = occupation_groups
            params["occupation_group_codes"] = [uri.split('/C')[-1] for uri in occupation_groups]
        
        if schemes:
            params["schemes"] = schemes
        
        results = self.neo4j_client.run_query(query, params)
        
        occupations = []
        for rec in results:
            # Filter out empty skills (from OPTIONAL MATCH)
            required_skills = [
                s for s in rec["required_skills"] 
                if s["uri"] is not None
            ]
            
            occupations.append({
                "uri": rec["uri"],
                "label": rec["label"],
                "description": rec["description"],
                "isco_code": rec["isco_code"],
                "required_skills": required_skills,
                "groups": [g for g in rec["groups"] if g],
                "schemes": [s for s in rec["schemes"] if s]
            })
        
        return occupations
