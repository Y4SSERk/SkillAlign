# ml_pipeline/graph_builder.py

from __future__ import annotations

from pathlib import Path
from typing import List, Dict

import networkx as nx
import pandas as pd

from app.core.config import settings


def _clean_quotes(s: str) -> str:
    if s is None:
        return ""
    s = str(s).strip()
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        s = s[1:-1].strip()
    return s


def build_esco_graph(
    occupations_path: Path,
    relations_path: Path,
    skills_path: Path,
    output_path: Path,
) -> nx.DiGraph:
    """
    Build a directed ESCO knowledge graph:

    Nodes:
      - occupation_uri (type='occupation', preferredLabel)
      - skillUri (type='skill', preferredLabel)

    Edges:
      occupationUri -> skillUri, with attribute 'relation' (e.g. essential/optional).
    """

    print("--- Graph Builder: Starting graph construction ---")

    try:
        occupations_df = pd.read_csv(occupations_path, dtype=str).fillna("")
        relations_df = pd.read_csv(relations_path, dtype=str).fillna("")
        skills_df = pd.read_csv(skills_path, dtype=str).fillna("")
    except FileNotFoundError as e:
        print(f"FATAL: graph building failed. Missing file: {e}")
        raise

    # Basic schema checks (fail fast if ESCO exports change)
    for col in ["conceptUri", "preferredLabel"]:
        if col not in occupations_df.columns:
            raise ValueError(f"Missing '{col}' in occupations file: {occupations_path}")

    for col in ["conceptUri", "preferredLabel"]:
        if col not in skills_df.columns:
            raise ValueError(f"Missing '{col}' in skills file: {skills_path}")

    for col in ["occupationUri", "skillUri", "relationType"]:
        if col not in relations_df.columns:
            raise ValueError(f"Missing '{col}' in relations file: {relations_path}")

    # Clean occupation URIs and labels
    occupations_df["conceptUri"] = occupations_df["conceptUri"].astype(str).apply(_clean_quotes).str.strip()
    occupations_df["preferredLabel"] = occupations_df["preferredLabel"].astype(str).apply(_clean_quotes).str.strip()

    # Drop empty and duplicate occupation URIs
    before_occ = len(occupations_df)
    occupations_df = occupations_df[occupations_df["conceptUri"].astype(bool)]
    dropped_occ = before_occ - len(occupations_df)
    if dropped_occ:
        print(f"[graph] Dropped {dropped_occ} occupation rows with empty conceptUri.")

    if occupations_df["conceptUri"].duplicated().any():
        dup_count = occupations_df["conceptUri"].duplicated(keep=False).sum()
        print(f"[graph] Found {dup_count} duplicate occupation URIs, keeping first.")
        occupations_df = occupations_df.drop_duplicates(subset=["conceptUri"], keep="first")

    # Clean skills URIs and labels
    skills_df["conceptUri"] = skills_df["conceptUri"].astype(str).apply(_clean_quotes).str.strip()
    skills_df["preferredLabel"] = skills_df["preferredLabel"].astype(str).apply(_clean_quotes).str.strip()

    before_sk = len(skills_df)
    skills_df = skills_df[skills_df["conceptUri"].astype(bool)]
    dropped_sk = before_sk - len(skills_df)
    if dropped_sk:
        print(f"[graph] Dropped {dropped_sk} skill rows with empty conceptUri.")

    if skills_df["conceptUri"].duplicated().any():
        dup_sk = skills_df["conceptUri"].duplicated(keep=False).sum()
        print(f"[graph] Found {dup_sk} duplicate skill URIs, keeping first.")
        skills_df = skills_df.drop_duplicates(subset=["conceptUri"], keep="first")

    # Build directed graph
    G = nx.DiGraph()

    # Add occupation nodes
    occ_nodes = occupations_df[["conceptUri", "preferredLabel"]].copy()
    occ_nodes["type"] = "occupation"
    for _, row in occ_nodes.iterrows():
        nid = row["conceptUri"]
        G.add_node(
            nid,
            preferredLabel=row["preferredLabel"],
            type=row["type"],
        )

    print(f"[graph] Added {occ_nodes.shape[0]} occupation nodes.")

    # Add skill nodes
    skill_nodes = skills_df[["conceptUri", "preferredLabel"]].copy()
    skill_nodes["type"] = "skill"
    added_skills = 0
    for _, row in skill_nodes.iterrows():
        nid = row["conceptUri"]
        attrs = {
            "preferredLabel": row["preferredLabel"],
            "type": row["type"],
        }
        if nid in G:
            G.nodes[nid].update(attrs)
        else:
            G.add_node(nid, **attrs)
            added_skills += 1

    print(f"[graph] Added {added_skills} skill nodes (some may merge with occupations).")

    # Add edges occupationUri -> skillUri
    relations_clean = relations_df[["occupationUri", "skillUri", "relationType"]].copy()
    edge_count = 0
    for _, row in relations_clean.iterrows():
        source = _clean_quotes(row["occupationUri"]).strip()
        target = _clean_quotes(row["skillUri"]).strip()
        relation = str(row["relationType"]).strip().lower().replace(" ", "_")

        if source and target and source in G and target in G:
            G.add_edge(source, target, relation=relation)
            edge_count += 1

    print(f"[graph] Added {edge_count} edges from occupations to skills.")

    # Save graph
    output_path.parent.mkdir(parents=True, exist_ok=True)
    nx.write_gml(G, str(output_path))
    print(f"[graph] Final graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges.")
    print(f"[graph] Graph saved to: {output_path}")

    return G


def load_esco_graph(path: Path) -> nx.DiGraph:
    """
    Load the saved graph file (GML) and return a NetworkX DiGraph.
    """
    if not path.exists():
        raise FileNotFoundError(f"Graph file not found: {path}")
    G = nx.read_gml(str(path))
    # ensure node ids are strings
    G = nx.relabel_nodes(G, lambda n: str(n))
    return G


def find_required_skills_for_occupation(
    G: nx.DiGraph,
    occupation_uri: str,
    required_labels: tuple[str, ...] = ("essential",),
) -> List[Dict[str, str]]:
    """
    Given a graph and occupation URI, return a list of required skills.

    Looks at outgoing edges from the occupation node and selects edges whose
    'relation' attribute contains any of the strings in required_labels.
    Returns:
      [
        { "skill_uri": ..., "skill_label": ..., "relation_type": ... },
        ...
      ]
    """
    results: List[Dict[str, str]] = []
    if occupation_uri not in G:
        return results

    for nbr in G.successors(occupation_uri):
        edge_data = G.get_edge_data(occupation_uri, nbr) or {}
        relation = edge_data.get("relation", "")
        rel_norm = str(relation).lower()

        if any(lbl in rel_norm for lbl in required_labels):
            skill_label = G.nodes[nbr].get("preferredLabel", "") or G.nodes[nbr].get("label", "")
            results.append(
                {
                    "skill_uri": str(nbr),
                    "skill_label": str(skill_label),
                    "relation_type": relation,
                }
            )

    return results
