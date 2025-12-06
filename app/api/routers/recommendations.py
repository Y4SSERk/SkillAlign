from fastapi import APIRouter, Depends

from app.api.models import SkillInput, RecommendationResponse
from app.api.deps import get_model, get_faiss_index, get_metadata_df
from app.api.services.recommendation_service import get_recommendations

router = APIRouter(tags=["recommendations"])


@router.post("/recommendations", response_model=RecommendationResponse)
async def recommendations_endpoint(
    payload: SkillInput,
    model=Depends(get_model),
    faiss_index=Depends(get_faiss_index),
    metadata_df=Depends(get_metadata_df),
):
    recs = get_recommendations(
        payload.skills,
        payload.top_k,
        model,
        faiss_index,
        metadata_df,
    )
    return RecommendationResponse(recommendations=recs)
