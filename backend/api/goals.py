from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from database import get_db
from models.learner import Learner
from core.deps import get_current_learner
from schemas.roadmap import GoalResponse
from services.goal_service import (
    get_learner_goals, 
    create_goal, 
    activate_goal, 
    delete_goal
)

router = APIRouter()

class GoalCreatePayload(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    target_role: str = Field(..., min_length=2, max_length=200)
    timeline_months: int = Field(6, ge=1, le=36)
    set_active: bool = True

@router.get("", response_model=List[GoalResponse])
def list_goals(
    current_learner: Learner = Depends(get_current_learner),
    db: Session = Depends(get_db)
):
    """List all saved learning goals for the authenticated learner."""
    return get_learner_goals(db, current_learner.id)

@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
def add_goal(
    payload: GoalCreatePayload,
    current_learner: Learner = Depends(get_current_learner),
    db: Session = Depends(get_db)
):
    """Add a new learning goal (up to 3 max) and generate its roadmap."""
    return create_goal(
        db=db,
        learner_id=current_learner.id,
        title=payload.title.strip(),
        target_role=payload.target_role.strip(),
        timeline_months=payload.timeline_months,
        set_active=payload.set_active
    )

@router.put("/{goal_id}/activate", response_model=GoalResponse)
def activate_learner_goal(
    goal_id: int,
    current_learner: Learner = Depends(get_current_learner),
    db: Session = Depends(get_db)
):
    """Switch active goal and prepare its roadmap."""
    return activate_goal(db, current_learner.id, goal_id)

@router.delete("/{goal_id}")
def remove_learner_goal(
    goal_id: int,
    current_learner: Learner = Depends(get_current_learner),
    db: Session = Depends(get_db)
):
    """Delete a goal and its dependent data with last-goal protection."""
    return delete_goal(db, current_learner.id, goal_id)
