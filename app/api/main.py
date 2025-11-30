from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from pathlib import Path
import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from app.core.config import settings 
from app.api.models import SkillInput, OccupationRecommendation, RecommendationResponse, SkillGapResponse, SkillGapItem

import networkx as nx
from ml_pipeline.graph_builder import load_esco_graph, find_required_skills_for_occupation
from urllib.parse import unquote

# --- Global Assets ---
# These are loaded only once when the application starts up
model: SentenceTransformer = None
faiss_index: faiss.Index = None
metadata_df: pd.DataFrame = None
esco_graph: nx.Graph = None

# --- Application Initialization ---
app = FastAPI(
    title="SkillAlign Job Recommendation API",
    description="Backend API for matching user skills to ESCO occupations using vector embeddings and FAISS search.",
    version="1.0.0"
)

# --- Lifespan Context Manager ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup (loading ML assets) and shutdown events for the application.
    """
    global model, faiss_index, metadata_df, esco_graph
    
    # --- STARTUP LOGIC (Your existing load_ml_assets function) ---
    # 1. Load Sentence Transformer Model
    print(f"Loading Sentence Transformer model: {settings.MODEL_NAME}")
    try:
        model = SentenceTransformer(settings.MODEL_NAME)
    except Exception as e:
        print(f"FATAL: Could not load model {settings.MODEL_NAME}. Error: {e}")
        raise

    # 2. Load FAISS Index
    index_path = Path(settings.FAISS_INDEX_PATH)
    print(f"Loading FAISS index from: {index_path}")
    if index_path.exists():
        faiss_index = faiss.read_index(str(index_path))
    else:
        raise FileNotFoundError(f"FAISS index not found at {index_path}")

    # 3. Load Metadata
    metadata_path = index_path.parent / "occupation_metadata.csv"
    print(f"Loading metadata from: {metadata_path}")
    if metadata_path.exists():
        metadata_df = pd.read_csv(metadata_path)
    else:
        raise FileNotFoundError(f"Metadata file not found at {metadata_path}")

    # Load the ESCO knowledge graph
    graph_path = Path(settings.PROCESSED_DATA_DIR) / "esco_knowledge_graph.gml"
    print(f"Loading ESCO knowledge graph from: {graph_path}")
    if graph_path.exists():
        esco_graph = load_esco_graph(graph_path)
        print(f"Graph loaded: nodes={esco_graph.number_of_nodes()}, edges={esco_graph.number_of_edges()}")
    else:
        print(f"Warning: ESCO graph not found at {graph_path}; graph endpoints will be unavailable.")

    print("ML assets loaded successfully. API is ready.")
    
    # The 'yield' signals that the startup phase is complete, and the server can now accept requests.
    yield
    
    # --- SHUTDOWN LOGIC (Add cleanup here if needed later) ---
    print("Application shutting down.")
    
# --- Application Initialization ---
app = FastAPI(
    # CRITICAL CHANGE: Pass the lifespan function to the FastAPI constructor
    lifespan=lifespan,
    title="SkillAlign Job Recommendation API",
    description="Backend API for matching user skills to ESCO occupations...",
    version="1.0.0"
)


# --- Endpoints ---

@app.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(input: SkillInput):
    """
    Accepts a list of user skills and returns the top_k most relevant occupations
    based on vector similarity search.
    """
    if faiss_index is None or metadata_df is None or model is None:
        raise HTTPException(
            status_code=503, 
            detail="ML assets are not loaded. Check server startup logs for errors."
        )

    # 1. Prepare and Encode Input Text
    # Join user skills into a single string for embedding
    user_input_text = ". ".join(input.skill_input)
    
    # Encode the user input
    user_embedding = model.encode(user_input_text, convert_to_numpy=True)
    user_embedding = user_embedding.astype('float32').reshape(1, -1)

    # 2. Perform FAISS Search (top_k nearest neighbors)
    k = input.top_k
    # D: Distances (lower is better, as we used L2/Euclidean distance)
    # I: Indices (the internal ID of the vector in the index)
    D, I = faiss_index.search(user_embedding, k)
    
    recommended_indices = I[0]
    distances = D[0]
    
    # 3. Map Results back to Metadata
    recommendations = []
    
    # The FAISS index ID corresponds to the row index in the original embeddings 
    # and should be an implicit index in the metadata_df.
    
    for rank, (index_id, distance) in enumerate(zip(recommended_indices, distances)):
        # Look up the row by index
        job_metadata = metadata_df.iloc[index_id]
        
        recommendations.append(
            OccupationRecommendation(
                job_title=job_metadata['preferredLabel'],
                esco_uri=job_metadata['conceptUri'],
                # Convert distance to a similarity score (inverse of distance for user understanding)
                # Note: We use 1 / (1 + distance) to scale the score between 0 and 1,
                # where 1 is perfect similarity (distance 0).
                similarity_score=1 / (1 + distance) 
            )
        )
        
    return RecommendationResponse(recommendations=recommendations)

@app.get("/occupation/skill-gap/{occupation_uri:path}", response_model=SkillGapResponse)
async def get_skill_gap_analysis(occupation_uri: str):
    """
    Returns essential/required skills for the given occupation URI using the ESCO graph.
    Accepts full URIs (unencoded or URL-encoded) and tries several tolerant matches.
    """
    if esco_graph is None:
        raise HTTPException(status_code=503, detail="ESCO graph not loaded.")

    # Try raw and URL-decoded forms plus simple normalized variants
    candidate_raw = occupation_uri
    candidate_decoded = unquote(occupation_uri)
    candidates = [
        candidate_raw,
        candidate_decoded,
        candidate_raw.strip('"').strip("'"),
        candidate_decoded.strip('"').strip("'")
    ]

    # also try switching http/https and removing trailing slash
    def variants(u: str):
        u = u or ''
        u = u.rstrip('/')
        v = [u]
        if u.startswith('http://'):
            v.append('https://' + u[len('http://'):])
        elif u.startswith('https://'):
            v.append('http://' + u[len('https://'):])
        return v

    final_candidates = []
    for c in candidates:
        final_candidates.extend(variants(c))

    # deduplicate while preserving order
    seen = set()
    final_list = []
    for c in final_candidates:
        if c and c not in seen:
            seen.add(c)
            final_list.append(c)

    found_node = None
    for c in final_list:
        if c in esco_graph:
            found_node = c
            break

    # As a last resort, try to match by node attribute 'conceptUri' if nodes use different ids
    if not found_node:
        for node_id, attrs in esco_graph.nodes(data=True):
            node_concept = str(attrs.get('conceptUri', '')).strip()
            for c in final_list:
                if c == node_concept:
                    found_node = node_id
                    break
            if found_node:
                break

    if not found_node:
        raise HTTPException(
            status_code=404,
            detail=(
                "Occupation URI not found in ESCO graph. "
                "Ensure you URL-encode the full URI when calling the endpoint or "
                "use an occupation URI that exists in the graph."
            )
        )

    # find required skills (uses graph traversal helper)
    skill_entries = find_required_skills_for_occupation(esco_graph, found_node)

    items = [
        SkillGapItem(
            skill_uri=e['skill_uri'],
            skill_label=e.get('skill_label', ''),
            relation_type=e.get('relation_type', '')
        ) for e in skill_entries
    ]

    occupation_title = esco_graph.nodes[found_node].get('preferredLabel', '')

    return SkillGapResponse(
        occupation_uri=found_node,
        occupation_title=occupation_title,
        required_skills=items
    )