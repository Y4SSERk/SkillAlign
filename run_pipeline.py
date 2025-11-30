import sys
import time
from pathlib import Path

# To ensure imports work when running from the project root
sys.path.append('.')

from ml_pipeline.data_ingestion import ingest_all_data
from ml_pipeline.data_processing import clean_and_merge_data 
from ml_pipeline.embedding_generator import generate_and_index_embeddings
# NEW IMPORT: Add the graph builder function
from ml_pipeline.graph_builder import build_esco_graph 
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

        # 2. Data Processing (Returns the final unified DataFrame)
        print("\n--- STAGE 2: Data Processing ---")
        occupations_df = clean_and_merge_data(raw_data)

        if occupations_df is None or occupations_df.empty:
            print("Error: Occupations data is empty after processing.")
            return

        # 2.5. Graph Construction (NEW STAGE)
        print("\n--- STAGE 2.5: Graph Construction ---")
        
        # Define paths for the files needed for graph edges (relations)
        occupation_metadata_path = Path(settings.PROCESSED_DATA_DIR) / "occupation_metadata.csv"
        relations_path = Path(settings.RAW_DATA_DIR) / "occupationSkillRelations_en.csv"
        skills_path = Path(settings.RAW_DATA_DIR) / "skills_en.csv"
        graph_output_path = Path(settings.PROCESSED_DATA_DIR) / "esco_knowledge_graph.gml"
        
        # The occupations_df data is saved to occupation_metadata.csv inside clean_and_merge_data.
        # We ensure it exists before proceeding to the graph step.
        
        esco_graph = build_esco_graph(
            occupations_path=occupation_metadata_path,
            relations_path=relations_path,
            skills_path=skills_path,
            output_path=graph_output_path
        )
        print(f"Knowledge Graph built with {esco_graph.number_of_nodes()} nodes and {esco_graph.number_of_edges()} edges.")
        
        # 3. Modeling and Indexing
        print("\n--- STAGE 3: Modeling and Indexing ---")
        # The embedding_generator needs the dataframe containing 'text_for_embedding'
        generate_and_index_embeddings(occupations_df)

        end_time = time.time()
        duration = end_time - start_time
        print("\n" + "="*60)
        print(f"✅ Pipeline Completed Successfully in {duration:.2f} seconds.")
        print("The FAISS index and Knowledge Graph are ready for the FastAPI backend.")
        print("="*60)

    except FileNotFoundError as e:
        print(f"\nFATAL ERROR: {e}")
        print("Please ensure all required ESCO CSV files are in the data/raw directory.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_ml_pipeline()