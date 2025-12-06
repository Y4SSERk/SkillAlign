from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.api import state
from app.api.routers import recommendations_router, graph_router
from ml_pipeline.graph_builder import load_esco_graph


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting application startup: loading ML assets")

    # Model
    print(f"Loading Sentence Transformer model: {settings.MODEL_NAME}")
    state.model = SentenceTransformer(settings.MODEL_NAME)

    # FAISS index
    idx_path = Path(settings.FAISS_INDEX_PATH)
    print(f"Loading FAISS index from: {idx_path}")
    state.faiss_index = faiss.read_index(str(idx_path))

    # Metadata
    meta_path = idx_path.parent / "occupation_metadata.csv"
    print(f"Loading metadata from: {meta_path}")
    state.metadata_df = pd.read_csv(meta_path)

    # ESCO graph
    graph_path = Path(settings.PROCESSED_DATA_DIR) / "esco_knowledge_graph.gml"
    print(f"Loading ESCO knowledge graph from: {graph_path}")
    state.esco_graph = load_esco_graph(graph_path)
    print(
        f"Graph loaded: nodes={state.esco_graph.number_of_nodes()}, edges={state.esco_graph.number_of_edges()}"
    )

    print("ML assets loaded successfully. API is ready.")
    yield
    print("Shutdown: cleaning up if necessary")


app = FastAPI(
    title="SkillAlign API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(recommendations_router)
app.include_router(graph_router)  # NO EXTRA PREFIX - graph.py handles it

@app.get("/health", tags=["health"])
async def health():
    return {
        "status": "healthy",
        "model_loaded": state.model is not None,
        "faiss_index_loaded": state.faiss_index is not None,
        "metadata_rows": len(state.metadata_df) if state.metadata_df is not None else 0,
        "graph_nodes": state.esco_graph.number_of_nodes() if state.esco_graph is not None else 0,
    }
