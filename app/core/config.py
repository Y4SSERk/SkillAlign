from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Data Paths ---
    ESCO_DATA_DIR: str = Field(
        default="./data/raw",
        description="Directory for raw ESCO CSV files.",
    )
    RAW_DATA_DIR: str = Field(
        default="./data/raw",
        description="Directory for raw ESCO CSV files (alias of ESCO_DATA_DIR).",
    )
    PROCESSED_DATA_DIR: str = Field(
        default="./data/processed",
        description="Directory for processed artifacts (metadata, indexes, graphs).",
    )

    # --- ML Artifacts ---
    FAISS_INDEX_PATH: str = Field(
        default="./data/processed/occupation.index",
        description="Path to the pre-computed FAISS index.",
    )
    MODEL_NAME: str = Field(
        default="sentence-transformers/all-mpnet-base-v2",
        description="Hugging Face model ID for embeddings.",
    )

    # --- App ---
    ENVIRONMENT: str = Field(
        default="development",
        description="Application environment (development/production).",
    )
    UVICORN_PORT: int = Field(
        default=8000,
        description="Port for the FastAPI application.",
    )


settings = Settings()
