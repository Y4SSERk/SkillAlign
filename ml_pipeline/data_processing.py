# ml_pipeline/data_processing.py

from __future__ import annotations

import pandas as pd


def clean_and_merge_data(raw_data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Build a clean occupation table with:
    - occupation_uri
    - occupation_label
    - text_for_embedding (label + description + definition + aggregated skills)

    using ESCO occupations (core + research), skills, and occupation-skill relations.
    Assumes standard ESCO exports as described in the PRD v3.
    """
    print("Starting data cleaning and preparation...")

    # 1) Get dataframes from ingestion
    occ_core = raw_data["occupations_core"].copy()
    occ_research = raw_data["occupations_research"].copy()
    skills_df = raw_data["skills_core"].copy()
    relations_df = raw_data["occupation_skill_relations"].copy()

    # 1.1) Concatenate core and research occupations, then drop dupes on conceptUri
    occupations_df = pd.concat([occ_core, occ_research], ignore_index=True)
    print("Occupations columns:", occupations_df.columns.tolist())

    if "conceptUri" not in occupations_df.columns or "preferredLabel" not in occupations_df.columns:
        raise ValueError(
            "Expected 'conceptUri' and 'preferredLabel' in occupations data."
        )

    occupations_df["conceptUri"] = occupations_df["conceptUri"].astype(str).str.strip()
    occupations_df["preferredLabel"] = (
        occupations_df["preferredLabel"].astype(str).str.strip()
    )
    occupations_df = occupations_df.drop_duplicates(subset=["conceptUri"], keep="first")

    # 2) Clean skills table (URI + lowercase name)
    if "conceptUri" not in skills_df.columns or "preferredLabel" not in skills_df.columns:
        raise ValueError(
            "Expected 'conceptUri' and 'preferredLabel' in skills_core data."
        )

    skills_clean = (
        skills_df[["conceptUri", "preferredLabel"]]
        .rename(
            columns={
                "conceptUri": "skillUri",
                "preferredLabel": "skill_name",
            }
        )
        .assign(
            skill_name=lambda df: df["skill_name"]
            .astype(str)
            .str.strip()
            .str.lower()
        )
    )

    # 3) Clean relations table (occupationUri, skillUri)
    for col in ("occupationUri", "skillUri"):
        if col not in relations_df.columns:
            raise ValueError(
                f"Expected '{col}' in occupation_skill_relations data."
            )

    relations_clean = relations_df[["occupationUri", "skillUri"]].copy()

    # 4) Join skills onto relations and aggregate per occupation
    skill_relations = relations_clean.merge(
        skills_clean,
        on="skillUri",
        how="left",
    )

    occupation_skills = (
        skill_relations.groupby("occupationUri")["skill_name"]
        .apply(lambda s: " ".join(s.dropna().astype(str)))
        .reset_index(name="aggregated_skills")
    )

    # 5) Clean occupations table and join aggregated skills
    for col in ("description", "definition"):
        if col not in occupations_df.columns:
            occupations_df[col] = ""

    occupations_df["description"] = occupations_df["description"].fillna("")
    occupations_df["definition"] = occupations_df["definition"].fillna("")

    merged = occupations_df.merge(
        occupation_skills,
        left_on="conceptUri",
        right_on="occupationUri",
        how="left",
    )

    merged["aggregated_skills"] = (
        merged["aggregated_skills"].fillna("").astype(str)
    )

    # 6) Build unified text_for_embedding
    merged["text_for_embedding"] = (
        merged["preferredLabel"].astype(str).str.lower()
        + ". "
        + merged["description"].astype(str).str.lower()
        + ". "
        + merged["definition"].astype(str).str.lower()
        + ". "
        + merged["aggregated_skills"].astype(str)
    )

    # 7) Final clean metadata for backend + embeddings
    final_df = merged[
        ["conceptUri", "preferredLabel", "text_for_embedding"]
    ].copy()

    final_df = final_df.rename(
        columns={
            "conceptUri": "occupation_uri",
            "preferredLabel": "occupation_label",
        }
    )

    print(f"Data processing complete. Final DataFrame size: {len(final_df)} rows.")
    return final_df
