from fastapi import HTTPException
from app.api import state


def get_model():
    if state.model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return state.model


def get_faiss_index():
    if state.faiss_index is None:
        raise HTTPException(status_code=503, detail="FAISS index not loaded")
    return state.faiss_index


def get_metadata_df():
    if state.metadata_df is None:
        raise HTTPException(status_code=503, detail="Metadata not loaded")
    return state.metadata_df


def get_esco_graph():
    if state.esco_graph is None:
        raise HTTPException(status_code=503, detail="ESCO graph not loaded")
    return state.esco_graph
