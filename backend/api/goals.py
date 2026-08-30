from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models.learner import Learner
from models.roadmap import LearnerGoal, Roadmap
from core.deps import get_current_learner, verify_learner_access
from schemas.roadmap import GoalRequest, GoalResponse
from services.goal_service import get_learner_goals, create_goal, activate_goal, delete_goal
from services.roadmap_service import generate_roadmap
from pydantic import BaseModel

router = APIRouter()

class GoalCreatePayload(BaseModel):
    title: str
    target_role: str
    timeline_months: int = 6
    set_active: bool = True

class GoalDeleteResponse(BaseModel):
    status: str
    message: str
    deleted_goal_id: int
    active_goal: Optional[GoalResponse] = None
    remaining_goals: List[GoalResponse] = []

@router.get("", response_model=List[GoalResponse])
def list_goals(
    db: Session = Depends(get_db),
    current_learner: Learner = Depends(get_current_learner)
):
    """List all goals for the authenticated learner."""
    return get_learner_goals(db, current_learner.id)

@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
def add_goal(
    payload: GoalCreatePayload,
    db: Session = Depends(get_db),
    current_learner: Learner = Depends(get_current_learner)
):
    """Create a new goal for the authenticated learner and generate its roadmap."""
    goal = create_goal(
        db,
        learner_id=current_learner.id,
        title=payload.title,
        target_role=payload.target_role,
        timeline_months=payload.timeline_months,
        set_active=payload.set_active
    )
    # Automatically generate corresponding roadmap for this new goal
    generate_roadmap(db, current_learner.id, goal_id=goal.id)
    return goal

@router.put("/{goal_id}/activate", response_model=GoalResponse)
@router.post("/{goal_id}/activate", response_model=GoalResponse)
def switch_active_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_learner: Learner = Depends(get_current_learner)
):
    """Switch active goal to goal_id."""
    goal = activate_goal(db, current_learner.id, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
        
    # Ensure roadmap exists for the newly activated goal
    rm = db.query(Roadmap).filter(
        Roadmap.learner_id == current_learner.id,
        Roadmap.goal_id == goal.id,
        Roadmap.status.in_(["active", "completed"])
    ).first()
    if not rm:
        generate_roadmap(db, current_learner.id, goal_id=goal.id)
        
    return goal

@router.delete("/{goal_id}", response_model=GoalDeleteResponse)
def remove_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_learner: Learner = Depends(get_current_learner)
):
    """Safely delete a specific goal and its associated learning-path data."""
    result = delete_goal(db, current_learner.id, goal_id)
    if not result:
        raise HTTPException(status_code=404, detail="Goal not found")
        
    return GoalDeleteResponse(
        status="success",
        message="Goal and its associated roadmap deleted successfully",
        deleted_goal_id=result["deleted_goal_id"],
        active_goal=result["active_goal"],
        remaining_goals=result["remaining_goals"]
    )

