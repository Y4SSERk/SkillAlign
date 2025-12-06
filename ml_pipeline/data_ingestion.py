import pandas as pd
from pathlib import Path
from app.core.config import settings


def load_esco_data(filename: str) -> pd.DataFrame:
    """
    Load a single ESCO CSV file into a Pandas DataFrame.

    Uses sep=None + engine='python' to auto-detect the delimiter and parse
    the header correctly.
    """
    esco_data_path = Path(settings.ESCO_DATA_DIR)
    file_path = esco_data_path / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"Required ESCO file not found: {file_path}. "
            f"Ensure it is in the {esco_data_path} directory."
        )

    print(f"Loading {filename}...")

    df = pd.read_csv(
        file_path,
        sep=None,            # auto-detects ',' vs ';'
        engine="python",     # required when sep=None
        encoding="utf-8-sig",
    )

    print(f"{filename} columns:", df.columns.tolist())
    return df


def ingest_all_data() -> dict[str, pd.DataFrame]:
    """
    Load all necessary ESCO files (occupations, skills, and occupation-skill relations)
    into a dict of DataFrames.
    """
    raw_data: dict[str, pd.DataFrame] = {}

    raw_data["occupations"] = load_esco_data("occupations_en.csv")
    raw_data["skills"] = load_esco_data("skills_en.csv")
    raw_data["relations"] = load_esco_data("occupationSkillRelations_en.csv")

    print("All necessary ESCO files ingested.")
    return raw_data
