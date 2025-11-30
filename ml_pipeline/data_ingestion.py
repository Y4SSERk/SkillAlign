import pandas as pd
import os
from pathlib import Path 
from app.core.config import settings

def load_esco_data(filename: str) -> pd.DataFrame:
    """
    Loads a single ESCO CSV file into a Pandas DataFrame, using robust 
    settings to handle BOM and bad lines, letting Pandas detect the header.
    """
    
    esco_data_path = Path(settings.ESCO_DATA_DIR)
    file_path: Path = esco_data_path / filename
    
    if not file_path.exists():
        raise FileNotFoundError(f"Required ESCO file not found: {file_path}. Ensure it is in the {esco_data_path} directory.")

    print(f"Loading {filename}...")
    
    try:
        df = pd.read_csv(
            file_path, 
            sep=';',              # ESCO standard delimiter
            encoding='utf-8-sig', # CRITICAL FIX: Handles and strips the Byte Order Mark (BOM)
            engine='python',      # Use Python engine for better complex line handling
            on_bad_lines='skip',  # Skips malformed lines
        )
    except Exception as e:
        # Fallback for older Pandas versions
        if "on_bad_lines" in str(e):
            print("Warning: Falling back to deprecated error handling for older Pandas version.")
            df = pd.read_csv(
                file_path, 
                sep=';', 
                encoding='utf-8-sig', 
                engine='python', 
                error_bad_lines=False,
                warn_bad_lines=True
            )
        else:
            raise e
            
    return df

def ingest_all_data() -> dict:
    """
    Loads all necessary ESCO files (Occupations, Skills, and their Relations).
    """
    raw_data = {}
    
    raw_data['occupations'] = load_esco_data('occupations_en.csv') 
    raw_data['skills'] = load_esco_data('skills_en.csv')
    raw_data['relations'] = load_esco_data('occupationSkillRelations_en.csv')

    print("All necessary ESCO files ingested.")
    return raw_data