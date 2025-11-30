import pandas as pd
import networkx as nx
from pathlib import Path
import re
from app.core.config import settings

def _clean_quotes(s: str) -> str:
    if s is None:
        return ''
    s = str(s).strip()
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        s = s[1:-1].strip()
    return s

def build_esco_graph(
    occupations_path: Path, 
    relations_path: Path, 
    skills_path: Path, 
    output_path: Path
) -> nx.Graph:
    """
    Builds a NetworkX graph from the cleaned ESCO CSV files (Occupations, Skills, Relations).
    Deduplicates by conceptUri and cleans surrounding quotes before creating nodes.
    """
    print("--- Graph Builder: Starting Graph Construction ---")

    # Load DataFrames with robust string handling
    try:
        occupations_df = pd.read_csv(occupations_path, dtype=str).fillna('')
        relations_df = pd.read_csv(relations_path, dtype=str).fillna('')
        skills_df = pd.read_csv(skills_path, dtype=str).fillna('')
    except FileNotFoundError as e:
        print(f"FATAL: Graph building failed. Missing file: {e}")
        raise

    # Clean and normalize important columns
    if 'conceptUri' in occupations_df.columns:
        occupations_df['conceptUri'] = occupations_df['conceptUri'].astype(str).apply(_clean_quotes).str.strip()
    else:
        occupations_df['conceptUri'] = occupations_df.iloc[:, 0].astype(str).apply(_clean_quotes).str.strip()

    # Preferred label: try existing column else choose a short-text candidate
    if 'preferredLabel' in occupations_df.columns:
        occupations_df['preferredLabel'] = occupations_df['preferredLabel'].astype(str).apply(_clean_quotes).str.strip()
    else:
        # fallback: pick a short text-like column
        for c in occupations_df.columns:
            if c != 'conceptUri' and occupations_df[c].astype(str).str.split().str.len().median() <= 6:
                occupations_df['preferredLabel'] = occupations_df[c].astype(str).apply(_clean_quotes).str.strip()
                break
        occupations_df['preferredLabel'] = occupations_df.get('preferredLabel', occupations_df.iloc[:, 1] if occupations_df.shape[1] > 1 else '').astype(str).apply(_clean_quotes).str.strip()

    # Drop empty URIs and deduplicate (keep first)
    before = len(occupations_df)
    occupations_df = occupations_df[occupations_df['conceptUri'].astype(bool)]
    dropped_empty = before - len(occupations_df)
    if dropped_empty:
        print(f"[fix] Dropped {dropped_empty} occupation rows with empty conceptUri.")

    dup_count = occupations_df['conceptUri'].duplicated(keep=False).sum()
    if dup_count:
        print(f"[fix] Found {dup_count} duplicate occupation conceptUri entries — keeping first occurrence.")
        occupations_df = occupations_df.drop_duplicates(subset=['conceptUri'], keep='first')

    # Prepare occupation nodes and set node attributes
    G = nx.DiGraph()
    occ_nodes = occupations_df[['conceptUri', 'preferredLabel']].copy()
    occ_nodes['type'] = 'occupation'
    # Explicitly add nodes with attributes (set_node_attributes does not create nodes)
    occ_attrs = occ_nodes.set_index('conceptUri').to_dict('index')
    for nid, attrs in occ_attrs.items():
        G.add_node(nid, **attrs)
    print(f"Added {len(occ_attrs)} occupation nodes.")
    
    # Clean skills frame similarly
    if 'conceptUri' in skills_df.columns:
        skills_df['conceptUri'] = skills_df['conceptUri'].astype(str).apply(_clean_quotes).str.strip()
    else:
        skills_df['conceptUri'] = skills_df.iloc[:, 0].astype(str).apply(_clean_quotes).str.strip()

    if 'preferredLabel' in skills_df.columns:
        skills_df['preferredLabel'] = skills_df['preferredLabel'].astype(str).apply(_clean_quotes).str.strip()
    else:
        skills_df['preferredLabel'] = skills_df['preferredLabel'].astype(str).apply(_clean_quotes).str.strip() if skills_df.shape[1] > 1 else ''
    
    # Drop empty URIs and deduplicate skills
    before_sk = len(skills_df)
    skills_df = skills_df[skills_df['conceptUri'].astype(bool)]
    dropped_empty_sk = before_sk - len(skills_df)
    if dropped_empty_sk:
        print(f"[fix] Dropped {dropped_empty_sk} skill rows with empty conceptUri.")
    dup_count_sk = skills_df['conceptUri'].duplicated(keep=False).sum()
    if dup_count_sk:
        print(f"[fix] Found {dup_count_sk} duplicate skill conceptUri entries — keeping first occurrence.")
        skills_df = skills_df.drop_duplicates(subset=['conceptUri'], keep='first')

    # Add skill nodes (avoid overwriting occupation nodes; merge attributes if collision)
    skill_nodes = skills_df[['conceptUri', 'preferredLabel']].copy()
    skill_nodes['type'] = 'skill'
    skill_attrs = skill_nodes.set_index('conceptUri').to_dict('index')
    added_skills = 0
    for nid, attrs in skill_attrs.items():
        if nid in G:
            # update existing node attrs (keep existing 'type' if occupation; add skill attrs)
            G.nodes[nid].update(attrs)
        else:
            G.add_node(nid, **attrs)
            added_skills += 1
    print(f"Added {added_skills} new skill nodes (merged with occupations where IDs collided).")

    # Add Edges
    relations_to_add = relations_df[['occupationUri', 'skillUri', 'relationType']].dropna(how='all')
    for index, row in relations_to_add.iterrows():
        source = _clean_quotes(str(row.get('occupationUri', ''))).strip()
        target = _clean_quotes(str(row.get('skillUri', ''))).strip()
        relation_type = str(row.get('relationType', '')).lower().replace(' ', '_')
        if source and target and source in G and target in G:
            G.add_edge(source, target, relation=relation_type)

    # Save graph
    output_path.parent.mkdir(parents=True, exist_ok=True)
    nx.write_gml(G, str(output_path))
    print(f"Successfully built graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
    print(f"Graph saved to: {output_path}")

    return G

def load_esco_graph(path: Path) -> nx.Graph:
    """
    Load the saved graph file (GML) and return NetworkX graph.
    """
    if not Path(path).exists():
        raise FileNotFoundError(f"Graph file not found: {path}")
    G = nx.read_gml(str(path))
    # ensure node ids are strings (consistent with earlier code)
    G = nx.relabel_nodes(G, lambda n: str(n))
    return G

def find_required_skills_for_occupation(G: nx.Graph, occupation_uri: str, required_labels: tuple = ('essential',)) -> list[dict]:
    """
    Given a graph and occupation URI, return a list of required skills.
    Looks at outgoing edges from the occupation node and selects edges
    whose 'relation' attribute matches any value in required_labels (case-insensitive substring).
    Returns list of dicts: {'skill_uri','skill_label','relation_type'}
    """
    results = []
    if occupation_uri not in G:
        return results

    for nbr in G.successors(occupation_uri):
        edge_data = G.get_edge_data(occupation_uri, nbr) or {}
        relation = edge_data.get('relation', '') or edge_data.get('relationType', '')
        rel_norm = str(relation).lower()
        # match if any required label appears in relation string
        if any(lbl in rel_norm for lbl in required_labels):
            skill_label = G.nodes[nbr].get('preferredLabel', '') or G.nodes[nbr].get('label', '')
            results.append({
                'skill_uri': str(nbr),
                'skill_label': str(skill_label),
                'relation_type': relation
            })
    return results

# Note: The raw relations file (`occupationSkillRelations_en.csv`) contains the 
# 'relationType' which specifies essential, optional, etc.[cite: 29, 62]