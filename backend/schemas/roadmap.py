from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from .resource import ResourceResponse, ProjectResponse

class GoalRequest(BaseModel):
    title: str
    target_role: str
    timeline_months: int

class GoalResponse(GoalRequest):
    id: int
    learner_id: int
    status: str
    created_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class MilestoneItemResponse(BaseModel):
    id: int
    milestone_id: int
    item_type: str
    status: str
    resource: Optional[ResourceResponse] = None
    project: Optional[ProjectResponse] = None
    completed_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class MilestoneResponse(BaseModel):
    id: int
    roadmap_id: int
    order_index: int
    title: str
    objective: Optional[str] = ""
    status: str
    estimated_hours: Optional[float] = 20.0
    skill_ids: Optional[List[int]] = []
    completion_criteria: Optional[str] = ""
    items: Optional[List[MilestoneItemResponse]] = []
    
    model_config = ConfigDict(from_attributes=True)

class RoadmapResponse(BaseModel):
    id: int
    learner_id: int
    goal_id: int
    status: str
    milestones: Optional[List[MilestoneResponse]] = []
    
    model_config = ConfigDict(from_attributes=True)

class NextActionResponse(BaseModel):
    action_type: str
    title: str
    description: str
    item_id: Optional[int] = None
    resource: Optional[ResourceResponse] = None
    project: Optional[ProjectResponse] = None
