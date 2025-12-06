from typing import Optional

import pandas as pd
import faiss
import networkx as nx
from sentence_transformers import SentenceTransformer


# Global app state (set in lifespan)
model: Optional[SentenceTransformer] = None
faiss_index: Optional[faiss.Index] = None
metadata_df: Optional[pd.DataFrame] = None
esco_graph: Optional[nx.Graph] = None
