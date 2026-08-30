from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class LearnerBase(BaseModel):
    name: str
    email: Optional[str] = None
    experience_level: Optional[str] = "beginner"
    weekly_hours: Optional[float] = 10.0
    learning_style: Optional[str] = None
    preferred_formats: Optional[List[str]] = []

class LearnerCreate(BaseModel):
    name: str
    email: Optional[str] = None
    experience_level: Optional[str] = "beginner"
    weekly_hours: Optional[float] = 10.0
    learning_style: Optional[str] = None
    preferred_formats: Optional[List[str]] = []

class LearnerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    experience_level: Optional[str] = None
    weekly_hours: Optional[float] = None
    learning_style: Optional[str] = None
    preferred_formats: Optional[List[str]] = None

class LearnerResponse(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    experience_level: Optional[str] = "beginner"
    weekly_hours: Optional[float] = 10.0
    learning_style: Optional[str] = None
    preferred_formats: Optional[List[str]] = []
    created_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class OnboardingRequest(BaseModel):
    goal_text: str

class OnboardingResponse(BaseModel):
    goal_id: Optional[int] = None
    goal: str
    target_role: str
    timeline_months: int
    experience_level: Optional[str] = "beginner"
    weekly_hours: Optional[float] = 10.0
    known_skills: Optional[List[str]] = []
    learning_style: Optional[str] = None
    preferred_formats: Optional[List[str]] = []
