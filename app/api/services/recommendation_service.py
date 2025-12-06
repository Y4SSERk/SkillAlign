# app/api/services/recommendation_service.py

from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import pandas as pd

from app.api.models import RecommendationItem


def get_recommendations(
    skills: List[str],
    top_k: int,
    model: SentenceTransformer,
    index: faiss.Index,
    metadata_df: pd.DataFrame,
) -> list[RecommendationItem]:
    """
    Get occupation recommendations based on user skills using FAISS semantic search.
    """
    if not skills:
        return []

    # Encode skills and average embeddings
    embeddings = model.encode(
        skills,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    user_vec = np.mean(embeddings, axis=0).astype("float32").reshape(1, -1)

    # FAISS similarity search (L2 distance)
    distances, indices = index.search(user_vec, top_k)

    recs: list[RecommendationItem] = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx < 0 or idx >= len(metadata_df):
            continue

        row = metadata_df.iloc[idx]
        
        # ✅ Use NEW metadata columns from pipeline
        occupation_uri = str(row["occupation_uri"])
        occupation_label = str(row["occupation_label"])
        
        # Convert distance to similarity score (0-1 range)
        similarity = float(1.0 / (1.0 + dist))

        recs.append(
            RecommendationItem(
                occupation_uri=occupation_uri,
                occupation_label=occupation_label,
                score=similarity,
            )
        )

    return recs
