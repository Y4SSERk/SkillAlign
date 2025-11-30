from pydantic import BaseModel, Field

# --- Request Models ---

class SkillInput(BaseModel):
    """Defines the structure for user input (a list of skills)."""
    skill_input: list[str] = Field(
        ..., 
        description="A list of skills provided by the user (e.g., ['Python', 'SQL', 'Deep Learning']).",
        example=["Python development", "Data visualization", "Machine learning modeling"]
    )
    top_k: int = Field(
        5, 
        description="The number of top recommendations to return.",
        ge=1, 
        le=50
    )

# --- Response Models ---

class OccupationRecommendation(BaseModel):
    """Defines the structure for a single occupation recommendation."""
    job_title: str = Field(..., description="The preferred label/title of the recommended occupation.")
    esco_uri: str = Field(..., description="The unique ESCO URI for the occupation concept.")
    similarity_score: float = Field(..., description="The Euclidean distance between the user input and the occupation embedding (lower is better).")


class RecommendationResponse(BaseModel):
    """The main response structure for the recommendations endpoint."""
    recommendations: list[OccupationRecommendation]

class SkillGapItem(BaseModel):
    skill_uri: str = Field(..., description="ESCO URI of the skill.")
    skill_label: str = Field(..., description="Human-readable label of the skill.")
    relation_type: str = Field(..., description="Relation type (e.g. 'essential', 'optional').")

class SkillGapResponse(BaseModel):
    occupation_uri: str = Field(..., description="ESCO URI of the occupation.")
    occupation_title: str = Field(..., description="Preferred label/title of the occupation.")
    required_skills: list[SkillGapItem] = Field(..., description="List of required/essential skills for the occupation.")