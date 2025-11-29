# run_pipeline.py
import sys
import time

# To ensure imports work when running from the project root
sys.path.append('.')

from ml_pipeline.data_ingestion import ingest_all_data
from ml_pipeline.data_processing import clean_and_merge_data # <--- Renamed function
from ml_pipeline.embedding_generator import generate_and_index_embeddings
from app.core.config import settings

def run_ml_pipeline():
    """
    Executes the end-to-end ML pipeline for SkillAlign.
    """
    start_time = time.time()
    print("="*60)
    print("🚀 Starting SkillAlign ML Pipeline Execution 🚀")
    print(f"Configuration loaded for environment: {settings.ENVIRONMENT}")
    print("="*60)

    try:
        # 1. Data Ingestion
        print("\n--- STAGE 1: Data Ingestion ---")
        raw_data = ingest_all_data()

        # 2. Data Processing (This function now returns the final unified DataFrame)
        print("\n--- STAGE 2: Data Processing ---")
        occupations_df = clean_and_merge_data(raw_data) # <--- Using updated function

        if occupations_df is None or occupations_df.empty:
            print("Error: Occupations data is empty after processing.")
            return

        # 3. Modeling and Indexing
        print("\n--- STAGE 3: Modeling and Indexing ---")
        # The embedding_generator needs the dataframe containing 'text_for_embedding'
        generate_and_index_embeddings(occupations_df)

        end_time = time.time()
        duration = end_time - start_time
        print("\n" + "="*60)
        print(f"✅ Pipeline Completed Successfully in {duration:.2f} seconds.")
        print("The FAISS index is ready to be served by the FastAPI backend.")
        print("="*60)

    except FileNotFoundError as e:
        print(f"\nFATAL ERROR: {e}")
        print("Please place the required ESCO CSV files in the data/raw directory.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_ml_pipeline()