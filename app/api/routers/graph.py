# app/api/routers/graph.py
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Any
from app.api.deps import get_esco_graph
import logging


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/skill-gap/{occupation_uri:path}", response_model=Dict[str, List[Dict[str, str]]])
async def get_skill_gap_graph(
    occupation_uri: str, 
    esco_graph: Any = Depends(get_esco_graph)
):
    """Get essential and optional skills required for an occupation from ESCO knowledge graph."""
    print(f"Skill gap request for occupation: {occupation_uri}")
    
    try:
        # Validate URI format
        if not occupation_uri.startswith("http://data.europa.eu/esco/occupation/"):
            raise HTTPException(status_code=400, detail="Invalid occupation URI format")
        
        # Get occupation node
        if occupation_uri not in esco_graph.nodes:
            print(f"Occupation not found: {occupation_uri}")
            raise HTTPException(status_code=404, detail="Occupation not found")
        
        # Extract essential/optional skills via graph traversal
        essential_skills = []
        optional_skills = []
        
        # Get skills by relation type (FIXED: use 'essential' and 'optional')
        for source, target, edge_data in esco_graph.edges(occupation_uri, data=True):
            relation = edge_data.get('relation')
            
            # Get skill details from target node
            if target in esco_graph.nodes:
                skill_node = esco_graph.nodes[target]
                skill_label = skill_node.get('preferredLabel', target)
                
                skill_data = {
                    "uri": target,
                    "label": skill_label,
                    "type": relation
                }
                
                if relation == 'essential':
                    essential_skills.append(skill_data)
                elif relation == 'optional':
                    optional_skills.append(skill_data)
        
        result = {
            "essential_skills": essential_skills[:10],
            "optional_skills": optional_skills[:10]
        }
        
        print(f"Found {len(essential_skills)} essential, {len(optional_skills)} optional skills")
        return result
        
    except Exception as e:
        print(f"Skill gap error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Graph traversal failed: {str(e)}")
