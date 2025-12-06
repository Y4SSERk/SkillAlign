# ml_pipeline/data_processing.py

from __future__ import annotations

import pandas as pd


def clean_and_merge_data(raw_data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Build a clean occupation table with:
      - occupation_uri
      - occupation_label
      - text_for_embedding (label + description + definition + aggregated skills)
    from ESCO occupations, skills, and occupation-skill relations.

    Assumes the ESCO CSVs are well-formed (standard ESCO exports).
    """

    print("Starting data cleaning and preparation...")

    # 1) Use dataframes as provided (no complex header logic)
    occupations_df = raw_data["occupations"].copy()
    skills_df = raw_data["skills"].copy()
    relations_df = raw_data["relations"].copy()

    print("Occupations columns:", occupations_df.columns.tolist())

    # 2) Clean skills table (URI + lowercase name)
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
    occupations_df["description"] = occupations_df["description"].fillna("")
    occupations_df["definition"] = occupations_df["definition"].fillna("")

    merged = occupations_df.merge(
        occupation_skills,
        left_on="conceptUri",
        right_on="occupationUri",
        how="left",
    )

    merged["aggregated_skills"] = merged["aggregated_skills"].fillna("").astype(str)

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
    final_df = merged[["conceptUri", "preferredLabel", "text_for_embedding"]].copy()
    final_df = final_df.rename(
        columns={
            "conceptUri": "occupation_uri",
            "preferredLabel": "occupation_label",
        }
    )

    print(f"Data processing complete. Final DataFrame size: {len(final_df)} rows.")
    return final_df
