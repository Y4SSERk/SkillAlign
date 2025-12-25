# ml_pipeline/run_pipeline.py

import sys
import time
from pathlib import Path

sys.path.append(".")

from ml_pipeline.data_ingestion import ingest_all_data
from ml_pipeline.data_processing import clean_and_merge_data
from ml_pipeline.embedding_generator import generate_and_index_embeddings
from ml_pipeline.neo4j_etl import load_rich_esco_to_neo4j
from app.core.settings import get_settings


def run_ml_pipeline() -> None:
    """
    1) Ingest ESCO CSVs
    2) Clean & merge into occupation table
    3) Build / refresh rich ESCO graph in Neo4j (all 17 CSVs)
    4) Generate embeddings and FAISS index
    """
    start_time = time.time()
    settings = get_settings()

    print("=" * 60)
    print("🚀 Starting SkillAlign ML Pipeline Execution 🚀")
    print(f"Configuration loaded for environment: {settings.environment.upper()}")
    print(f"Using ESCO data directory: {settings.esco_data_dir}")
    print("=" * 60)

    try:
        # 1. Data Ingestion
        print("\n--- STAGE 1: Data Ingestion ---")
        raw_data = ingest_all_data()

        # 2. Data Processing
        print("\n--- STAGE 2: Data Processing ---")
        occupations_df = clean_and_merge_data(raw_data)
        if occupations_df is None or occupations_df.empty:
            print("Error: occupations data is empty after processing.")
            return

        processed_dir = Path(settings.processed_data_dir)
        processed_dir.mkdir(parents=True, exist_ok=True)

        occupation_metadata_path = processed_dir / "occupation_metadata.csv"
        occupations_df[["occupation_uri", "occupation_label"]].to_csv(
            occupation_metadata_path,
            index=False,
        )
        print(f"Saved occupation metadata to: {occupation_metadata_path}")

        # 3. Neo4j ETL (rich graph build)
        print("\n--- STAGE 3: Neo4j Graph ETL ---")
        load_rich_esco_to_neo4j(raw_data)

        # 4. Modeling and Indexing (embeddings + FAISS)
        print("\n--- STAGE 4: Modeling and Indexing ---")
        generate_and_index_embeddings(occupations_df)

        duration = time.time() - start_time
        print("\n" + "=" * 60)
        print(f"✅ Pipeline completed successfully in {duration:.2f} seconds.")
        print("Neo4j graph, FAISS index, and occupation metadata are ready.")
        print("=" * 60)

    except FileNotFoundError as e:
        print(f"\nFATAL ERROR: {e}")
        print(
            "Please ensure all required ESCO CSV files are in the directory "
            f"configured by ESCO_DATA_DIR (currently: {settings.esco_data_dir})."
        )
        sys.exit(1)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_ml_pipeline()
