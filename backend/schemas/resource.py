from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class ResourceResponse(BaseModel):
    id: int
    title: str
    type: str
    provider: str
    url: Optional[str]
    difficulty: str
    duration_hours: float
    quality_score: float
    description: str
    skill_ids: List[int]
    prerequisite_skill_ids: List[int]
    
    model_config = ConfigDict(from_attributes=True)

class ProjectResponse(BaseModel):
    id: int
    title: str
    description: str
    difficulty: str
    skill_ids: List[int]
    estimated_hours: float
    
    model_config = ConfigDict(from_attributes=True)

class RecommendationResponse(BaseModel):
    resource: ResourceResponse
    score: float
    score_breakdown: dict
    explanation: str
