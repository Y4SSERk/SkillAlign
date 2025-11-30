# ml_pipeline/embedding_generator.py
import pandas as pd
from pathlib import Path
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from app.core.config import settings

def generate_and_index_embeddings(occupations_df):
    """
    Generate embeddings for occupations and create/save a FAISS index.
    Defensive: ensure FAISS_INDEX_PATH is a Path, parent dir exists, and we ALWAYS
    pass a string path to faiss.write_index.
    """
    model_name = settings.MODEL_NAME
    print(f"Loading Sentence Transformer model: {model_name}")
    model = SentenceTransformer(model_name)

    texts = occupations_df['text_for_embedding'].astype(str).tolist()
    print("Generating embeddings for all occupations...")
    
    # Generate embeddings
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True, batch_size=32)

    dim = embeddings.shape[1]
    print(f"Creating FAISS Index (Dimension: {dim}, Count: {len(embeddings)})")

    # Create Index
    index = faiss.IndexFlatL2(dim)
    index = faiss.IndexIDMap(index)
    ids = np.arange(len(embeddings)).astype('int64')
    index.add_with_ids(embeddings, ids)

    # Defensive path handling
    index_path = Path(settings.FAISS_INDEX_PATH)
    
    # Ensure parent directory exists
    if index_path.parent and str(index_path.parent) != '':
        index_path.parent.mkdir(parents=True, exist_ok=True)

    # Save the FAISS Index
    try:
        faiss.write_index(index, str(index_path))
        print(f"FAISS index saved to: {index_path}")
    except Exception as e:
        fallback = Path('data/processed/occupation.index')
        fallback.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(index, str(fallback))
        print(f"Warning: Failed to write to {index_path}. Saved to fallback {fallback}. Error: {e}")

    # --- NEW: Save Metadata CSV (CRITICAL FOR API) ---
    # This saves the mapping between the Index ID and the Job Title/URI
    metadata_path = index_path.parent / "occupation_metadata.csv"
    
    print(f"Saving metadata to: {metadata_path}")
    # We save conceptUri (ID) and preferredLabel (Title)
    occupations_df[['conceptUri', 'preferredLabel']].to_csv(metadata_path, index=False)
    
    return index, ids