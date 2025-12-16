# app/core/settings.py
# Loads settings from file.env/.env using pydantic-settings.

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=("file.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Neo4j Connection ---
    neo4j_uri: str = Field(default="neo4j://127.0.0.1:7687", alias="NEO4J_URI")
    neo4j_user: str = Field(default="neo4j", alias="NEO4J_USER")
    neo4j_password: str = Field(default="", alias="NEO4J_PASSWORD")

    # --- Data Paths (ESCO CSVs etc.) ---
    esco_data_dir: Path = Field(default=Path("./data/esco"), alias="ESCO_DATA_DIR")
    processed_data_dir: Path = Field(default=Path("./data/processed"), alias="PROCESSED_DATA_DIR")

    # --- ML Model Artifacts ---
    faiss_index_path: Path = Field(
        default=Path("./data/processed/occupation.index"),
        alias="FAISS_INDEX_PATH",
    )
    model_name: str = Field(
        default="sentence-transformers/all-mpnet-base-v2",
        alias="MODEL_NAME",
    )

    # --- Application Settings ---
    environment: str = Field(default="development", alias="ENVIRONMENT")
    uvicorn_port: int = Field(default=8000, alias="UVICORN_PORT")

    @property
    def neo4j_auth(self) -> tuple[str, str]:
        return (self.neo4j_user, self.neo4j_password)

    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
