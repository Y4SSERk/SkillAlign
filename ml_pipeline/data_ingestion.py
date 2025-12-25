# ml_pipeline/data_ingestion.py

from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Dict

import pandas as pd

from app.core.settings import get_settings

# Allow very large fields in ESCO CSVs (e.g., conceptSchemes_en.csv)
csv.field_size_limit(sys.maxsize)


def load_esco_data(filename: str) -> pd.DataFrame:
    """
    Load a single ESCO CSV file into a Pandas DataFrame.

    Uses sep=None + engine='python' to auto-detect the delimiter and parse
    the header correctly for most files, with a special case for
    conceptSchemes_en.csv which may contain very large fields.
    """
    esco_data_path = Path(get_settings().esco_data_dir)
    file_path = esco_data_path / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"Required ESCO file not found: {file_path}. "
            f"Ensure it is in the {esco_data_path} directory."
        )

    print(f"Loading {filename}...")

    if filename == "conceptSchemes_en.csv":
        # Use explicit comma separator and C engine for better performance
        df = pd.read_csv(
            file_path,
            sep=",",
            engine="c",
            encoding="utf-8-sig",
        )
    else:
        df = pd.read_csv(
            file_path,
            sep=None,          # auto-detects ',' vs ';'
            engine="python",   # required when sep=None
            encoding="utf-8-sig",
        )

    print(f"{filename} columns:", df.columns.tolist())
    return df


def ingest_all_data() -> Dict[str, pd.DataFrame]:
    """
    Load all ESCO CSVs needed for the rich graph defined in the PRD v3.

    Returns a dict of DataFrames keyed by logical dataset name.
    """
    raw_data: Dict[str, pd.DataFrame] = {}

    # --- Core occupations and skills ---
    raw_data["occupations_core"] = load_esco_data("occupations_en.csv")
    raw_data["occupations_research"] = load_esco_data(
        "researchOccupationsCollection_en.csv"
    )
    raw_data["skills_core"] = load_esco_data("skills_en.csv")
    raw_data["occupation_skill_relations"] = load_esco_data(
        "occupationSkillRelations_en.csv"
    )

    # --- Skill relations, hierarchies, and groups ---
    raw_data["skill_skill_relations"] = load_esco_data(
        "skillSkillRelations_en.csv"
    )
    raw_data["skills_hierarchy"] = load_esco_data("skillsHierarchy_en.csv")
    raw_data["skills_broader_relations"] = load_esco_data(
        "broaderRelationsSkillPillar_en.csv"
    )
    raw_data["skill_groups"] = load_esco_data("skillGroups_en.csv")

    # --- Occupation groups and ISCO hierarchy ---
    raw_data["isco_groups"] = load_esco_data("ISCOGroups_en.csv")
    raw_data["occupation_broader_relations"] = load_esco_data(
        "broaderRelationsOccPillar_en.csv"
    )

    # --- Concept schemes and thematic skill collections ---
    raw_data["concept_schemes"] = load_esco_data("conceptSchemes_en.csv")
    raw_data["digital_skills"] = load_esco_data(
        "digitalSkillsCollection_en.csv"
    )
    raw_data["green_skills"] = load_esco_data("greenSkillsCollection_en.csv")
    raw_data["digcomp_skills"] = load_esco_data(
        "digCompSkillsCollection_en.csv"
    )
    raw_data["research_skills"] = load_esco_data(
        "researchSkillsCollection_en.csv"
    )
    raw_data["transversal_skills"] = load_esco_data(
        "transversalSkillsCollection_en.csv"
    )
    raw_data["language_skills"] = load_esco_data(
        "languageSkillsCollection_en.csv"
    )

    print("All ESCO files for the rich graph have been ingested.")
    return raw_data
