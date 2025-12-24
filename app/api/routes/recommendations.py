# app/api/routes/recommendations.py

"""
Recommendations API Routes
Endpoints for occupation recommendations based on skills.
"""

import logging
from fastapi import APIRouter, HTTPException, status

from app.core.deps import Neo4jDep
from app.core.ml import ml_engine
from app.api.services.recommendations import RecommendationsService
from app.api.schemas.recommendations import (
    RecommendationRequest,
    RecommendationResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.post(
    "",
    response_model=RecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get occupation recommendations",
    description="""
    Generate occupation recommendations based on a user's skills using FAISS vector search 
    and Neo4j skill-gap analysis.
    
    **Process:**
    1. Encodes user skills into embeddings using SentenceTransformer
    2. Searches FAISS index for similar occupations
    3. Fetches occupation details from Neo4j
    4. Computes matched and missing skills for each occupation
    5. Applies optional filters (occupation groups, schemes)
    6. Returns ranked recommendations with skill-gap analysis
    
    **Filters:**
    - `occupation_groups`: Filter by ISCO occupation groups
    - `schemes`: Filter by concept schemes (Digital, Green, Research, etc.)
    """
)
def get_recommendations(
    request: RecommendationRequest,
    neo4j_client: Neo4jDep
) -> RecommendationResponse:
    """
    Get occupation recommendations based on user skills.
    
    Args:
        request: Recommendation request with skills and optional filters
        neo4j_client: Neo4j client (injected)
    
    Returns:
        RecommendationResponse with recommended occupations and skill-gap analysis
    
    Raises:
        HTTPException 503: If ML resources (FAISS/model) are not ready
        HTTPException 400: If input validation fails
        HTTPException 500: If recommendation generation fails
    """
    # Check if ML engine is ready
    if not ml_engine.is_ready():
        logger.error("ML engine is not ready")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Recommendation engine is not ready. Please ensure FAISS index and model are loaded."
        )
    
    # Generate recommendations
    try:
        service = RecommendationsService(neo4j_client)
        response = service.get_recommendations(request)
        
        logger.info(
            f"Generated {response.total} recommendations for "
            f"{len(request.skills)} skills"
        )
        
        return response
        
    except ValueError as e:
        logger.warning(f"Invalid recommendation request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error(f"Failed to generate recommendations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )
