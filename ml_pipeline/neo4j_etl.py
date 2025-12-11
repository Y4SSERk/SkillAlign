# ml_pipeline/neo4j_etl.py

from __future__ import annotations

import os
from typing import Dict, List

import pandas as pd
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()  # expects NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD in .env


def load_rich_esco_to_neo4j(raw_data: Dict[str, pd.DataFrame]) -> None:
    """
    Load the full ESCO graph into Neo4j, matching the rich model in the PRD v3
    and using all 17 CSV files.

    Nodes:
      - :Occupation { uri, preferredLabel, description, iscoCode, status }
      - :Skill { uri, preferredLabel, description, skillType, reuseLevel, status }
      - :SkillGroup { uri, label, description, status, code }
      - :OccupationGroup { uri, code, label, description, status }
      - :ConceptScheme { uri, label, status, description }

    Relationships:
      - (:Occupation)-[:REQUIRES { relation, skillType }]->(:Skill)
      - (:Skill)-[:RELATED_SKILL { relationType }]->(:Skill)
      - (:Skill)-[:IN_SKILL_GROUP]->(:SkillGroup)
      - (:SkillGroup)-[:BROADER_THAN_SKILL_GROUP]->(:SkillGroup)
      - (:Occupation)-[:IN_OCC_GROUP]->(:OccupationGroup)
      - (:OccupationGroup)-[:BROADER_THAN_OCC_GROUP]->(:OccupationGroup)
      - (:Occupation)-[:IN_SCHEME]->(:ConceptScheme)
      - (:Skill)-[:IN_SCHEME]->(:ConceptScheme)

    Additional properties from thematic collections (all 6 CSVs):
      - s.inDigitalSkillsCollection
      - s.inGreenSkillsCollection
      - s.inDigCompSkillsCollection
      - s.inResearchSkillsCollection
      - s.inTransversalSkillsCollection
      - s.inLanguageSkillsCollection
    """

    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")

    driver = GraphDatabase.driver(uri, auth=(user, password))

    # --- Core dataframes ---
    occ_core = raw_data["occupations_core"].copy()
    occ_research = raw_data["occupations_research"].copy()
    skills = raw_data["skills_core"].copy()
    relations = raw_data["occupation_skill_relations"].copy()

    # --- Extra dataframes for richness (hierarchies, groups, schemes) ---
    skill_skill_rel = raw_data["skill_skill_relations"].copy()
    skills_hierarchy = raw_data["skills_hierarchy"].copy()
    skill_groups = raw_data["skill_groups"].copy()
    skills_broader = raw_data["skills_broader_relations"].copy()
    isco_groups = raw_data["isco_groups"].copy()
    occ_broader = raw_data["occupation_broader_relations"].copy()
    concept_schemes = raw_data["concept_schemes"].copy()

    # --- Thematic skill collections (6 CSVs) ---
    digital_skills = raw_data["digital_skills"].copy()
    green_skills = raw_data["green_skills"].copy()
    digcomp_skills = raw_data["digcomp_skills"].copy()
    research_skills = raw_data["research_skills"].copy()
    transversal_skills = raw_data["transversal_skills"].copy()
    language_skills = raw_data["language_skills"].copy()

    # Clean NAs
    occupations = pd.concat([occ_core, occ_research], ignore_index=True).fillna("")
    skills = skills.fillna("")
    relations = relations.fillna("")
    skill_skill_rel = skill_skill_rel.fillna("")
    skills_hierarchy = skills_hierarchy.fillna("")
    skill_groups = skill_groups.fillna("")
    skills_broader = skills_broader.fillna("")
    isco_groups = isco_groups.fillna("")
    occ_broader = occ_broader.fillna("")
    concept_schemes = concept_schemes.fillna("")
    digital_skills = digital_skills.fillna("")
    green_skills = green_skills.fillna("")
    digcomp_skills = digcomp_skills.fillna("")
    research_skills = research_skills.fillna("")
    transversal_skills = transversal_skills.fillna("")
    language_skills = language_skills.fillna("")

    # Precompute URI sets for type checks
    occ_uris = set(occupations["conceptUri"].astype(str).str.strip())
    skill_uris = set(skills["conceptUri"].astype(str).str.strip())
    skill_group_uris = set(skill_groups["conceptUri"].astype(str).str.strip())
    occ_group_uris = set(isco_groups["conceptUri"].astype(str).str.strip())

    def create_constraints(tx):
        # Neo4j 5.x syntax: FOR / REQUIRE
        tx.run(
            """
            CREATE CONSTRAINT occupation_uri_unique IF NOT EXISTS
            FOR (o:Occupation)
            REQUIRE o.uri IS UNIQUE
            """
        )
        tx.run(
            """
            CREATE CONSTRAINT skill_uri_unique IF NOT EXISTS
            FOR (s:Skill)
            REQUIRE s.uri IS UNIQUE
            """
        )
        tx.run(
            """
            CREATE CONSTRAINT skillgroup_uri_unique IF NOT EXISTS
            FOR (g:SkillGroup)
            REQUIRE g.uri IS UNIQUE
            """
        )
        tx.run(
            """
            CREATE CONSTRAINT occgroup_uri_unique IF NOT EXISTS
            FOR (g:OccupationGroup)
            REQUIRE g.uri IS UNIQUE
            """
        )
        tx.run(
            """
            CREATE CONSTRAINT scheme_uri_unique IF NOT EXISTS
            FOR (cs:ConceptScheme)
            REQUIRE cs.uri IS UNIQUE
            """
        )

    def load_occupations(tx, rows: List[dict]):
        tx.run(
            """
            UNWIND $rows AS row
            MERGE (o:Occupation {uri: row.uri})
            SET  o.preferredLabel = row.label,
                 o.description   = row.description,
                 o.iscoCode      = row.iscoCode,
                 o.status        = row.status
            """,
            rows=rows,
        )

    def load_skills(tx, rows: List[dict]):
        tx.run(
            """
            UNWIND $rows AS row
            MERGE (s:Skill {uri: row.uri})
            SET  s.preferredLabel = row.label,
                 s.description   = row.description,
                 s.skillType     = row.skillType,
                 s.reuseLevel    = row.reuseLevel,
                 s.status        = row.status
            """,
            rows=rows,
        )

    def load_requires(tx, rows: List[dict]):
        tx.run(
            """
            UNWIND $rows AS row
            MATCH (o:Occupation {uri: row.occupationUri})
            MATCH (s:Skill {uri: row.skillUri})
            MERGE (o)-[r:REQUIRES]->(s)
            SET   r.relation  = row.relationType,
                  r.skillType = row.skillType
            """,
            rows=rows,
        )

    def load_skill_groups(tx, rows: List[dict]):
        tx.run(
            """
            UNWIND $rows AS row
            MERGE (g:SkillGroup {uri: row.uri})
            SET  g.label       = row.label,
                 g.description = row.description,
                 g.status      = row.status,
                 g.code        = row.code
            """,
            rows=rows,
        )

    def load_skill_group_membership(tx, rows: List[dict]):
        tx.run(
            """
            UNWIND $rows AS row
            MATCH (s:Skill {uri: row.skillUri})
            MATCH (g:SkillGroup {uri: row.groupUri})
            MERGE (s)-[:IN_SKILL_GROUP]->(g)
            """,
            rows=rows,
        )

    def load_skill_group_hierarchy(tx, rows: List[dict]):
        tx.run(
            """
            UNWIND $rows AS row
            MATCH (n:SkillGroup {uri: row.narrowUri})
            MATCH (b:SkillGroup {uri: row.broaderUri})
            MERGE (n)-[:BROADER_THAN_SKILL_GROUP]->(b)
            """,
            rows=rows,
        )

    def load_skill_relations(tx, rows: List[dict]):
        tx.run(
            """
            UNWIND $rows AS row
            MATCH (s1:Skill {uri: row.fromUri})
            MATCH (s2:Skill {uri: row.toUri})
            MERGE (s1)-[r:RELATED_SKILL]->(s2)
            SET   r.relationType = row.relationType
            """,
            rows=rows,
        )

    def load_occ_groups(tx, rows: List[dict]):
        tx.run(
            """
            UNWIND $rows AS row
            MERGE (g:OccupationGroup {uri: row.uri})
            SET  g.code        = row.code,
                 g.label       = row.label,
                 g.description = row.description,
                 g.status      = row.status
            """,
            rows=rows,
        )

    def load_in_occ_group(tx, rows: List[dict]):
        tx.run(
            """
            UNWIND $rows AS row
            MATCH (o:Occupation {uri: row.occUri})
            MATCH (g:OccupationGroup {uri: row.groupUri})
            MERGE (o)-[:IN_OCC_GROUP]->(g)
            """,
            rows=rows,
        )

    def load_occ_group_hierarchy(tx, rows: List[dict]):
        tx.run(
            """
            UNWIND $rows AS row
            MATCH (n:OccupationGroup {uri: row.narrowUri})
            MATCH (b:OccupationGroup {uri: row.broaderUri})
            MERGE (n)-[:BROADER_THAN_OCC_GROUP]->(b)
            """,
            rows=rows,
        )

    def load_concept_schemes(tx, rows: List[dict]):
        tx.run(
            """
            UNWIND $rows AS row
            MERGE (cs:ConceptScheme {uri: row.uri})
            SET  cs.label       = row.label,
                 cs.status      = row.status,
                 cs.description = row.description
            """,
            rows=rows,
        )

    def load_in_scheme_occ(tx, rows: List[dict]):
        tx.run(
            """
            UNWIND $rows AS row
            MATCH (o:Occupation {uri: row.occUri})
            MATCH (cs:ConceptScheme {uri: row.schemeUri})
            MERGE (o)-[:IN_SCHEME]->(cs)
            """,
            rows=rows,
        )

    def load_in_scheme_skill(tx, rows: List[dict]):
        tx.run(
            """
            UNWIND $rows AS row
            MATCH (s:Skill {uri: row.skillUri})
            MATCH (cs:ConceptScheme {uri: row.schemeUri})
            MERGE (s)-[:IN_SCHEME]->(cs)
            """,
            rows=rows,
        )

    # Thematic flags: one helper per collection
    def load_digital_flags(tx, rows: List[dict]):
        tx.run(
            """
            UNWIND $rows AS row
            MATCH (s:Skill {uri: row.skillUri})
            SET   s.inDigitalSkillsCollection = true
            """,
            rows=rows,
        )

    def load_green_flags(tx, rows: List[dict]):
        tx.run(
            """
            UNWIND $rows AS row
            MATCH (s:Skill {uri: row.skillUri})
            SET   s.inGreenSkillsCollection = true
            """,
            rows=rows,
        )

    def load_digcomp_flags(tx, rows: List[dict]):
        tx.run(
            """
            UNWIND $rows AS row
            MATCH (s:Skill {uri: row.skillUri})
            SET   s.inDigCompSkillsCollection = true
            """,
            rows=rows,
        )

    def load_research_flags(tx, rows: List[dict]):
        tx.run(
            """
            UNWIND $rows AS row
            MATCH (s:Skill {uri: row.skillUri})
            SET   s.inResearchSkillsCollection = true
            """,
            rows=rows,
        )

    def load_transversal_flags(tx, rows: List[dict]):
        tx.run(
            """
            UNWIND $rows AS row
            MATCH (s:Skill {uri: row.skillUri})
            SET   s.inTransversalSkillsCollection = true
            """,
            rows=rows,
        )

    def load_language_flags(tx, rows: List[dict]):
        tx.run(
            """
            UNWIND $rows AS row
            MATCH (s:Skill {uri: row.skillUri})
            SET   s.inLanguageSkillsCollection = true
            """,
            rows=rows,
        )

    with driver.session() as session:
        # 1) Constraints
        session.execute_write(create_constraints)

        # 2) Occupations
        occ_rows: List[dict] = [
            {
                "uri": str(r.get("conceptUri", "")).strip(),
                "label": str(r.get("preferredLabel", "")).strip(),
                "description": str(r.get("description", "")),
                "iscoCode": str(r.get("iscoGroup", "")),
                "status": str(r.get("status", "")),
            }
            for _, r in occupations.iterrows()
            if str(r.get("conceptUri", "")).strip()
        ]
        session.execute_write(load_occupations, occ_rows)

        # 3) Skills
        skill_rows: List[dict] = [
            {
                "uri": str(r.get("conceptUri", "")).strip(),
                "label": str(r.get("preferredLabel", "")).strip(),
                "description": str(r.get("description", "")),
                "skillType": str(r.get("skillType", "")),
                "reuseLevel": str(r.get("reuseLevel", "")),
                "status": str(r.get("status", "")),
            }
            for _, r in skills.iterrows()
            if str(r.get("conceptUri", "")).strip()
        ]
        session.execute_write(load_skills, skill_rows)

        # 4) Occupation–Skill REQUIRES
        requires_rows: List[dict] = [
            {
                "occupationUri": str(r.get("occupationUri", "")).strip(),
                "skillUri": str(r.get("skillUri", "")).strip(),
                "relationType": str(r.get("relationType", "")),
                "skillType": str(r.get("skillType", "")),
            }
            for _, r in relations.iterrows()
            if str(r.get("occupationUri", "")).strip()
            and str(r.get("skillUri", "")).strip()
        ]
        session.execute_write(load_requires, requires_rows)

        # 5) Skill groups
        sg_rows: List[dict] = [
            {
                "uri": str(r.get("conceptUri", "")).strip(),
                "label": str(r.get("preferredLabel", "")).strip(),
                "description": str(r.get("description", "")),
                "status": str(r.get("status", "")),
                "code": str(r.get("code", "")),
            }
            for _, r in skill_groups.iterrows()
            if str(r.get("conceptUri", "")).strip()
        ]
        session.execute_write(load_skill_groups, sg_rows)

        # 6) Skill–Skill relations (RELATED_SKILL)
        rel_skill_rows: List[dict] = [
            {
                "fromUri": str(r.get("originalSkillUri", "")).strip(),
                "toUri": str(r.get("relatedSkillUri", "")).strip(),
                "relationType": str(r.get("relationType", "")),
            }
            for _, r in skill_skill_rel.iterrows()
            if str(r.get("originalSkillUri", "")).strip()
            and str(r.get("relatedSkillUri", "")).strip()
        ]
        session.execute_write(load_skill_relations, rel_skill_rows)

        # 7) Skill–SkillGroup membership & group hierarchy from broaderRelationsSkillPillar
        sg_membership_rows: List[dict] = []
        sg_hierarchy_rows: List[dict] = []

        for _, r in skills_broader.iterrows():
            child = str(r.get("conceptUri", "")).strip()
            parent = str(r.get("broaderUri", "")).strip()
            if not child or not parent:
                continue

            if child in skill_uris and parent in skill_group_uris:
                sg_membership_rows.append(
                    {"skillUri": child, "groupUri": parent}
                )
            elif child in skill_group_uris and parent in skill_group_uris:
                sg_hierarchy_rows.append(
                    {"narrowUri": child, "broaderUri": parent}
                )

        if sg_membership_rows:
            session.execute_write(load_skill_group_membership, sg_membership_rows)
        if sg_hierarchy_rows:
            session.execute_write(load_skill_group_hierarchy, sg_hierarchy_rows)

        # 8) Additional SkillGroup hierarchy from skillsHierarchy_en.csv (Level 0–3)
        # Treat all level URIs as SkillGroup nodes and create broader-than edges L3->L2->L1->L0
        skill_hierarchy_edges: List[dict] = []
        for _, r in skills_hierarchy.iterrows():
            levels = [
                (str(r.get("Level 0 URI", "")).strip(), str(r.get("Level 0 preferred term", "")).strip()),
                (str(r.get("Level 1 URI", "")).strip(), str(r.get("Level 1 preferred term", "")).strip()),
                (str(r.get("Level 2 URI", "")).strip(), str(r.get("Level 2 preferred term", "")).strip()),
                (str(r.get("Level 3 URI", "")).strip(), str(r.get("Level 3 preferred term", "")).strip()),
            ]
            # create group nodes + edges between successive non-empty levels
            for idx in range(3, 0, -1):
                child_uri, child_label = levels[idx]
                parent_uri, parent_label = levels[idx - 1]
                if child_uri and parent_uri:
                    skill_hierarchy_edges.append(
                        {
                            "childUri": child_uri,
                            "childLabel": child_label,
                            "parentUri": parent_uri,
                            "parentLabel": parent_label,
                        }
                    )

        if skill_hierarchy_edges:
            session.execute_write(
                lambda tx, rows: tx.run(
                    """
                    UNWIND $rows AS row
                    MERGE (child:SkillGroup {uri: row.childUri})
                    SET   child.label = coalesce(child.label, row.childLabel)
                    MERGE (parent:SkillGroup {uri: row.parentUri})
                    SET   parent.label = coalesce(parent.label, row.parentLabel)
                    MERGE (child)-[:BROADER_THAN_SKILL_GROUP]->(parent)
                    """,
                    rows=rows,
                ),
                skill_hierarchy_edges,
            )

        # 9) Occupation groups (ISCO)
        occ_group_rows: List[dict] = [
            {
                "uri": str(r.get("conceptUri", "")).strip(),
                "code": str(r.get("code", "")),
                "label": str(r.get("preferredLabel", "")).strip(),
                "description": str(r.get("description", "")),
                "status": str(r.get("status", "")),
            }
            for _, r in isco_groups.iterrows()
            if str(r.get("conceptUri", "")).strip()
        ]
        session.execute_write(load_occ_groups, occ_group_rows)

        # 10) Occupation–group membership & group hierarchy from broaderRelationsOccPillar
        occ_in_group_rows: List[dict] = []
        occ_group_hierarchy_rows: List[dict] = []

        for _, r in occ_broader.iterrows():
            child = str(r.get("conceptUri", "")).strip()
            parent = str(r.get("broaderUri", "")).strip()
            if not child or not parent:
                continue

            if child in occ_uris and parent in occ_group_uris:
                occ_in_group_rows.append(
                    {"occUri": child, "groupUri": parent}
                )
            elif child in occ_group_uris and parent in occ_group_uris:
                occ_group_hierarchy_rows.append(
                    {"narrowUri": child, "broaderUri": parent}
                )

        if occ_in_group_rows:
            session.execute_write(load_in_occ_group, occ_in_group_rows)
        if occ_group_hierarchy_rows:
            session.execute_write(load_occ_group_hierarchy, occ_group_hierarchy_rows)

        # 11) Concept schemes
        scheme_rows: List[dict] = [
            {
                "uri": str(r.get("conceptSchemeUri", "")).strip(),
                "label": str(r.get("preferredLabel", "")).strip(),
                "status": str(r.get("status", "")),
                "description": str(r.get("description", "")),
            }
            for _, r in concept_schemes.iterrows()
            if str(r.get("conceptSchemeUri", "")).strip()
        ]
        session.execute_write(load_concept_schemes, scheme_rows)

        # 12) IN_SCHEME for occupations (using inScheme column)
        occ_in_scheme_rows: List[dict] = []
        for _, r in occupations.iterrows():
            occ_uri = str(r.get("conceptUri", "")).strip()
            if not occ_uri:
                continue
            schemes_str = str(r.get("inScheme", "")).strip()
            if not schemes_str:
                continue
            for sch in schemes_str.split():
                sch = sch.strip()
                if sch:
                    occ_in_scheme_rows.append(
                        {"occUri": occ_uri, "schemeUri": sch}
                    )

        if occ_in_scheme_rows:
            session.execute_write(load_in_scheme_occ, occ_in_scheme_rows)

        # 13) IN_SCHEME for skills (using inScheme column)
        skill_in_scheme_rows: List[dict] = []
        for _, r in skills.iterrows():
            skill_uri = str(r.get("conceptUri", "")).strip()
            if not skill_uri:
                continue
            schemes_str = str(r.get("inScheme", "")).strip()
            if not schemes_str:
                continue
            for sch in schemes_str.split():
                sch = sch.strip()
                if sch:
                    skill_in_scheme_rows.append(
                        {"skillUri": skill_uri, "schemeUri": sch}
                    )

        if skill_in_scheme_rows:
            session.execute_write(load_in_scheme_skill, skill_in_scheme_rows)

        # 14) Thematic skill collections -> boolean flags on :Skill
        def build_flag_rows(df: pd.DataFrame) -> List[dict]:
            return [
                {"skillUri": str(r.get("conceptUri", "")).strip()}
                for _, r in df.iterrows()
                if str(r.get("conceptUri", "")).strip()
            ]

        digital_rows = build_flag_rows(digital_skills)
        green_rows = build_flag_rows(green_skills)
        digcomp_rows = build_flag_rows(digcomp_skills)
        research_rows = build_flag_rows(research_skills)
        transversal_rows = build_flag_rows(transversal_skills)
        language_rows = build_flag_rows(language_skills)

        if digital_rows:
            session.execute_write(load_digital_flags, digital_rows)
        if green_rows:
            session.execute_write(load_green_flags, green_rows)
        if digcomp_rows:
            session.execute_write(load_digcomp_flags, digcomp_rows)
        if research_rows:
            session.execute_write(load_research_flags, research_rows)
        if transversal_rows:
            session.execute_write(load_transversal_flags, transversal_rows)
        if language_rows:
            session.execute_write(load_language_flags, language_rows)

    driver.close()
    print("✅ Rich ESCO graph (all 17 CSVs) loaded into Neo4j.")
