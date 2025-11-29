from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os
from dotenv import load_dotenv

# Load .env file (if it exists)
# This will load variables from the .env file into os.environ
load_dotenv()

# Define the Configuration Settings using Pydantic
class Settings(BaseSettings):
    # This defines where Pydantic should look for configuration data
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    # --- Data Paths ---
    ESCO_DATA_DIR: str = Field(
        default="./data/raw", 
        description="Directory for raw ESCO CSV files."
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
        default=os.environ.get("ENVIRONMENT", "development"),
        description="Application environment (development/production)."
    )
    
    UVICORN_PORT: int = Field(
        default=8000,
        description="Port for the FastAPI application."
    )

# Instantiate the settings object
settings = Settings()