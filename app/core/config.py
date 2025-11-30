from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Define the Configuration Settings using Pydantic
class Settings(BaseSettings):
    # This defines where Pydantic should look for configuration data
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    # --- Data Paths ---
    ESCO_DATA_DIR: str = Field(
        default="./data/raw", 
        description="Directory for raw ESCO CSV files."
    )
    # Added: explicit raw and processed dirs used across the pipeline
    RAW_DATA_DIR: str = Field(
        default="./data/raw",
        description="Directory for raw ESCO CSV files (alias of ESCO_DATA_DIR)."
    )
    PROCESSED_DATA_DIR: str = Field(
        default="./data/processed",
        description="Directory for processed artifacts (metadata, indexes, graphs)."
    )
    
    # --- ML Model Artifacts ---
    FAISS_INDEX_PATH: str = Field(
        default="./data/processed/occupation.index",
        description="Path to the pre-computed FAISS index."
    )
    
    MODEL_NAME: str = Field(
        default="sentence-transformers/all-mpnet-base-v2",
        description="Hugging Face model ID for embeddings."
    )

    # --- Application Settings ---
    ENVIRONMENT: str = Field(
        default="development",
        description="Application environment (development/production)."
    )
    
    UVICORN_PORT: int = Field(
        default=8000,
        description="Port for the FastAPI application."
    )

# Instantiate the settings object
settings = Settings()