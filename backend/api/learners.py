from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.learner import LearnerCreate, LearnerResponse, LearnerUpdate, OnboardingRequest, OnboardingResponse
from schemas.roadmap import GoalResponse, GoalRequest
from services.learner_service import create_learner, get_learner, update_learner
from services.goal_service import create_goal
from services.roadmap_service import get_next_action
from ai.provider import LLMProvider
from ai.onboarding import extract_goal_from_text
from models.roadmap import LearnerGoal
from models.skill import Skill, LearnerSkill
from recommendation.skill_gap import calculate_system_confidence
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()
llm = LLMProvider()

class CustomGoalUpdateRequest(BaseModel):
    title: str
    target_role: str
    timeline_months: int = 6
    known_skills: List[str] = []
    experience_level: Optional[str] = None
    weekly_hours: Optional[float] = None

@router.post("", response_model=LearnerResponse)
def create_new_learner(learner: LearnerCreate, db: Session = Depends(get_db)):
    return create_learner(db, learner)

@router.get("/{learner_id}", response_model=LearnerResponse)
def read_learner(learner_id: int, db: Session = Depends(get_db)):
    db_learner = get_learner(db, learner_id)
    if db_learner is None:
        raise HTTPException(status_code=404, detail="Learner not found")
    return db_learner

@router.put("/{learner_id}", response_model=LearnerResponse)
def update_existing_learner(learner_id: int, learner: LearnerUpdate, db: Session = Depends(get_db)):
    db_learner = update_learner(db, learner_id, learner)
    if db_learner is None:
        raise HTTPException(status_code=404, detail="Learner not found")
    return db_learner

@router.post("/{learner_id}/onboard", response_model=OnboardingResponse)
async def onboard_learner(learner_id: int, req: OnboardingRequest, db: Session = Depends(get_db)):
    db_learner = get_learner(db, learner_id)
    if not db_learner:
        raise HTTPException(status_code=404, detail="Learner not found")
        
    goal_data = await extract_goal_from_text(req.goal_text, llm)
    
    # Update learner profile
    if goal_data.get("experience_level"):
        db_learner.experience_level = goal_data["experience_level"]
    if goal_data.get("weekly_hours"):
        db_learner.weekly_hours = goal_data["weekly_hours"]
    if goal_data.get("learning_style"):
        db_learner.learning_style = goal_data["learning_style"]
    if goal_data.get("preferred_formats"):
        db_learner.preferred_formats = goal_data["preferred_formats"]
    db.commit()
    
    # Create goal with derived requirements
    goal_title = goal_data.get("title") or req.goal_text.strip().title()
    target_role = goal_data.get("target_role") or "Software Professional"
    timeline_months = int(goal_data.get("timeline_months") or 6)
    
    goal = create_goal(db, learner_id, goal_title, target_role, timeline_months)
    
    # Register known skills
    known_skills = goal_data.get("known_skills", [])
    if known_skills:
        skill_map = {s.name: s for s in db.query(Skill).all()}
        for skill_name in known_skills:
            if skill_name in skill_map:
                existing_ls = db.query(LearnerSkill).filter(
                    LearnerSkill.learner_id == learner_id,
                    LearnerSkill.skill_id == skill_map[skill_name].id
                ).first()
                if not existing_ls:
                    ls = LearnerSkill(
                        learner_id=learner_id,
                        skill_id=skill_map[skill_name].id,
                        self_reported_level=75.0,
                        system_confidence=calculate_system_confidence(75.0, None)
                    )
                    db.add(ls)
        db.commit()
        
    return OnboardingResponse(
        goal_id=goal.id,
        goal=goal.title,
        target_role=goal.target_role,
        timeline_months=goal.timeline_months,
        experience_level=db_learner.experience_level,
        weekly_hours=db_learner.weekly_hours,
        known_skills=known_skills,
        learning_style=db_learner.learning_style,
        preferred_formats=db_learner.preferred_formats or ["course", "practice"]
    )

@router.post("/{learner_id}/goal")
@router.put("/{learner_id}/goal")
def set_or_update_goal(learner_id: int, req: CustomGoalUpdateRequest, db: Session = Depends(get_db)):
    """Update learner goal and profile directly (used during Edit Manually)."""
    db_learner = get_learner(db, learner_id)
    if not db_learner:
        raise HTTPException(status_code=404, detail="Learner not found")
        
    if req.experience_level:
        db_learner.experience_level = req.experience_level
    if req.weekly_hours:
        db_learner.weekly_hours = req.weekly_hours
    db.commit()
    
    goal = create_goal(db, learner_id, req.title, req.target_role, req.timeline_months)
    
    # Update known skills
    skill_map = {s.name: s for s in db.query(Skill).all()}
    for skill_name in req.known_skills:
        if skill_name in skill_map:
            existing_ls = db.query(LearnerSkill).filter(
                LearnerSkill.learner_id == learner_id,
                LearnerSkill.skill_id == skill_map[skill_name].id
            ).first()
            if not existing_ls:
                ls = LearnerSkill(
                    learner_id=learner_id,
                    skill_id=skill_map[skill_name].id,
                    self_reported_level=75.0,
                    system_confidence=calculate_system_confidence(75.0, None)
                )
                db.add(ls)
    db.commit()
    
    return {
        "status": "success",
        "goal_id": goal.id,
        "title": goal.title,
        "target_role": goal.target_role,
        "timeline_months": goal.timeline_months
    }

@router.get("/{learner_id}/next-action")
def learner_next_action(learner_id: int, db: Session = Depends(get_db)):
    return get_next_action(db, learner_id)
