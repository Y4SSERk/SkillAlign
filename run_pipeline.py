import sys
import time
from pathlib import Path

# Ensure imports work when running from project root
sys.path.append(".")

from ml_pipeline.data_ingestion import ingest_all_data
from ml_pipeline.data_processing import clean_and_merge_data
from ml_pipeline.embedding_generator import generate_and_index_embeddings
from ml_pipeline.graph_builder import build_esco_graph
from app.core.config import settings


def run_ml_pipeline() -> None:
    """
    Execute the end-to-end ML pipeline for SkillAlign:

      1) Ingest ESCO CSVs
      2) Clean & merge into occupation table
      3) Build ESCO knowledge graph
      4) Generate embeddings and FAISS index
    """
    start_time = time.time()
    print("=" * 60)
    print("🚀 Starting SkillAlign ML Pipeline Execution 🚀")
    print(f"Configuration loaded for environment: {settings.ENVIRONMENT}")
    print("=" * 60)

    try:
        # 1. Data Ingestion
        print("\n--- STAGE 1: Data Ingestion ---")
        raw_data = ingest_all_data()

        # 2. Data Processing (returns unified occupation DataFrame)
        print("\n--- STAGE 2: Data Processing ---")
        occupations_df = clean_and_merge_data(raw_data)

        if occupations_df is None or occupations_df.empty:
            print("Error: occupations data is empty after processing.")
            return

        # Persist occupation metadata for the backend and graph step
        processed_dir = Path(settings.PROCESSED_DATA_DIR)
        processed_dir.mkdir(parents=True, exist_ok=True)

        occupation_metadata_path = processed_dir / "occupation_metadata.csv"
        occupations_df[["occupation_uri", "occupation_label"]].to_csv(
            occupation_metadata_path,
            index=False,
        )
        print(f"Saved occupation metadata to: {occupation_metadata_path}")

        # 2.5. Graph Construction
        print("\n--- STAGE 2.5: Graph Construction ---")

        relations_path = Path(settings.RAW_DATA_DIR) / "occupationSkillRelations_en.csv"
        skills_path = Path(settings.RAW_DATA_DIR) / "skills_en.csv"
        graph_output_path = processed_dir / "esco_knowledge_graph.gml"

        esco_graph = build_esco_graph(
            occupations_path=Path(settings.RAW_DATA_DIR) / "occupations_en.csv",
            relations_path=relations_path,
            skills_path=skills_path,
            output_path=graph_output_path,
        )
        print(
            f"Knowledge graph built with "
            f"{esco_graph.number_of_nodes()} nodes and "
            f"{esco_graph.number_of_edges()} edges."
        )

        # 3. Modeling and Indexing
        print("\n--- STAGE 3: Modeling and Indexing ---")
        generate_and_index_embeddings(occupations_df)

        duration = time.time() - start_time
        print("\n" + "=" * 60)
        print(f"✅ Pipeline completed successfully in {duration:.2f} seconds.")
        print("FAISS index, occupation metadata, and ESCO knowledge graph are ready.")
        print("=" * 60)

    except FileNotFoundError as e:
        print(f"\nFATAL ERROR: {e}")
        print("Please ensure all required ESCO CSV files are in the data/raw directory.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_ml_pipeline()
