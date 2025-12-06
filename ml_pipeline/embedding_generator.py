# ml_pipeline/embedding_generator.py

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

from app.core.config import settings


def generate_and_index_embeddings(occupations_df: pd.DataFrame) -> Tuple[faiss.Index, np.ndarray]:
    """
    Generate embeddings for occupations and create/save a FAISS index.

    Expects occupations_df to have:
      - occupation_uri
      - occupation_label
      - text_for_embedding
    """

    required_cols = ["occupation_uri", "occupation_label", "text_for_embedding"]
    for col in required_cols:
        if col not in occupations_df.columns:
            raise ValueError(f"Missing column '{col}' in occupations_df")

    model_name = settings.MODEL_NAME
    print(f"Loading Sentence Transformer model: {model_name}")
    model = SentenceTransformer(model_name)

    texts = occupations_df["text_for_embedding"].astype(str).tolist()
    print(f"Generating embeddings for {len(texts)} occupations...")

    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        convert_to_numpy=True,
        batch_size=32,
        normalize_embeddings=True,
    )

    dim = embeddings.shape[1]
    print(f"Creating FAISS index (dimension={dim}, count={len(embeddings)})")

    # Use a simple flat L2 index with explicit IDs aligned to row indices
    index = faiss.IndexFlatL2(dim)
    index = faiss.IndexIDMap(index)

    ids = np.arange(len(embeddings)).astype("int64")
    index.add_with_ids(embeddings, ids)

    # Handle index path
    index_path = Path(settings.FAISS_INDEX_PATH)
    if index_path.parent:
        index_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        faiss.write_index(index, str(index_path))
        print(f"FAISS index saved to: {index_path}")
    except Exception as e:
        fallback = Path("data/processed/occupation.index")
        fallback.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(index, str(fallback))
        print(
            f"Warning: Failed to write to {index_path}. "
            f"Saved to fallback {fallback}. Error: {e}"
        )
        index_path = fallback

    # Save clean metadata aligned with FAISS row order
    metadata_path = index_path.parent / "occupation_metadata.csv"
    print(f"Saving metadata to: {metadata_path}")

    occupations_df[["occupation_uri", "occupation_label"]].to_csv(
        metadata_path,
        index=False,
    )

    return index, ids
