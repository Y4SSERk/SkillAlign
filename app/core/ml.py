# app/core/ml.py

"""
ML Core Module
Handles loading and querying the FAISS index and SentenceTransformer model.
"""

import logging
from pathlib import Path
from typing import List, Tuple, Optional
import numpy as np
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class MLEngine:
    """
    Singleton ML engine for FAISS-based occupation recommendations.
    Loads the FAISS index and SentenceTransformer model on first access.
    """

    _instance: Optional["MLEngine"] = None
    _initialized: bool = False

    def __new__(cls) -> "MLEngine":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """
        Initialize the ML engine (lazy loading).
        Actual resources are loaded on first query.
        """
        if not self._initialized:
            self.faiss_index: Optional[faiss.Index] = None
            self.model: Optional[SentenceTransformer] = None
            self.occupation_uris: Optional[List[str]] = None
            self._initialized = True

    def _load_resources(self) -> None:
        """
        Load FAISS index, SentenceTransformer model, and occupation URI mapping.
        Raises RuntimeError if resources cannot be loaded.
        """
        if self.faiss_index is not None and self.model is not None:
            return  # Already loaded

        logger.info("Loading ML resources (FAISS index and SentenceTransformer model)...")

        # Load SentenceTransformer model FIRST (to know the expected dimension)
        model_name = "sentence-transformers/all-mpnet-base-v2"
        try:
            self.model = SentenceTransformer(model_name)
            model_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"SentenceTransformer model '{model_name}' loaded successfully. Embedding dimension: {model_dim}")
        except Exception as e:
            raise RuntimeError(f"Failed to load SentenceTransformer model: {e}") from e

        # Load FAISS index
        faiss_index_path = Path("data/processed/occupation.index")
        if not faiss_index_path.exists():
            raise RuntimeError(
                f"FAISS index not found at {faiss_index_path}. "
                "Please ensure the ML pipeline has been run to generate the index."
            )

        try:
            self.faiss_index = faiss.read_index(str(faiss_index_path))
            faiss_dim = self.faiss_index.d
            logger.info(
                f"FAISS index loaded successfully. "
                f"Index size: {self.faiss_index.ntotal} vectors, "
                f"Dimension: {faiss_dim}"
            )
            
            # Verify dimensions match
            if model_dim != faiss_dim:
                logger.error(
                    f"Dimension mismatch! Model produces {model_dim}-dim embeddings "
                    f"but FAISS index expects {faiss_dim}-dim vectors."
                )
                raise RuntimeError(
                    f"FAISS index dimension ({faiss_dim}) does not match "
                    f"model embedding dimension ({model_dim}). "
                    "Please rebuild the FAISS index with the correct model."
                )
        except Exception as e:
            raise RuntimeError(f"Failed to load FAISS index: {e}") from e

        # Load occupation metadata (URIs)
        metadata_path = Path("data/processed/occupation_metadata.csv")
        if not metadata_path.exists():
            raise RuntimeError(
                f"Occupation metadata not found at {metadata_path}. "
                "Please ensure the ML pipeline has generated occupation_metadata.csv."
            )

        try:
            metadata_df = pd.read_csv(metadata_path)
            
            # Extract occupation URIs
            if "occupation_uri" not in metadata_df.columns:
                raise RuntimeError(
                    f"Occupation metadata CSV must contain 'occupation_uri' column. "
                    f"Found columns: {list(metadata_df.columns)}"
                )
            
            self.occupation_uris = metadata_df["occupation_uri"].tolist()
            logger.info(f"Loaded {len(self.occupation_uris)} occupation URIs from metadata")

            # Sanity check: FAISS index size should match occupation URIs
            if len(self.occupation_uris) != self.faiss_index.ntotal:
                logger.warning(
                    f"Occupation URI count ({len(self.occupation_uris)}) does not match "
                    f"FAISS index size ({self.faiss_index.ntotal}). "
                    "Recommendations may be incorrect."
                )
        except Exception as e:
            raise RuntimeError(f"Failed to load occupation metadata: {e}") from e

        logger.info("ML resources loaded successfully")

    def encode(self, texts: List[str]) -> np.ndarray:
        """
        Encode a list of text strings into embeddings.

        Args:
            texts: List of text strings to encode

        Returns:
            numpy array of shape (len(texts), embedding_dim)
        """
        if self.model is None:
            self._load_resources()

        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        
        # Normalize embeddings (L2 normalization)
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        return embeddings

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 20
    ) -> List[Tuple[str, float]]:
        """
        Search FAISS index for top-k most similar occupations.

        Args:
            query_embedding: Query vector of shape (embedding_dim,) or (1, embedding_dim)
            top_k: Number of top results to return

        Returns:
            List of (occupation_uri, similarity_score) tuples, ordered by descending similarity
        """
        if self.faiss_index is None or self.occupation_uris is None:
            self._load_resources()

        # Ensure query embedding is 2D
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        # Ensure correct dtype
        query_embedding = query_embedding.astype(np.float32)
        
        # Verify dimension
        if query_embedding.shape[1] != self.faiss_index.d:
            raise RuntimeError(
                f"Query embedding dimension ({query_embedding.shape[1]}) "
                f"does not match FAISS index dimension ({self.faiss_index.d})"
            )

        # Perform FAISS search
        try:
            distances, indices = self.faiss_index.search(query_embedding, top_k)
        except Exception as e:
            logger.error(f"FAISS search failed: {e}")
            raise RuntimeError(f"FAISS search failed: {e}") from e

        # Map indices to occupation URIs and compute similarity scores
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < 0 or idx >= len(self.occupation_uris):
                logger.warning(f"Invalid FAISS index: {idx}")
                continue

            occupation_uri = self.occupation_uris[idx]
            
            # For normalized vectors and L2 distance:
            # similarity = 1 - (distance^2 / 2)
            # This converts L2 distance to cosine similarity for normalized vectors
            similarity_score = max(0.0, 1.0 - (distance * distance / 2.0))
            
            results.append((occupation_uri, float(similarity_score)))

        return results

    def is_ready(self) -> bool:
        """
        Check if ML resources are loaded and ready.

        Returns:
            True if FAISS index and model are loaded, False otherwise
        """
        try:
            self._load_resources()
            return (
                self.faiss_index is not None
                and self.model is not None
                and self.occupation_uris is not None
            )
        except Exception as e:
            logger.error(f"ML engine not ready: {e}")
            return False


# Singleton instance
ml_engine = MLEngine()
