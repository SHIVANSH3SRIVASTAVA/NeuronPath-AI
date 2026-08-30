from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class SkillBase(BaseModel):
    name: str
    category: str
    description: str

class SkillResponse(SkillBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

class LearnerSkillUpdate(BaseModel):
    self_reported_level: Optional[float] = None
    demonstrated_level: Optional[float] = None

class LearnerSkillResponse(BaseModel):
    id: int
    skill_id: int
    skill: SkillResponse
    self_reported_level: float
    demonstrated_level: Optional[float]
    system_confidence: float
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class SkillGapResponse(BaseModel):
    skill_id: int
    skill_name: str
    current_proficiency: float
    required_proficiency: float
    gap: float
    priority: float
