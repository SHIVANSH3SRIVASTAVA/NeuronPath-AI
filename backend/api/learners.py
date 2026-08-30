from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.learner import LearnerCreate, LearnerResponse, LearnerUpdate, OnboardingRequest, OnboardingResponse
from schemas.roadmap import GoalResponse, GoalRequest, RoadmapResponse
from services.learner_service import create_learner, get_learner, update_learner
from services.goal_service import create_goal
from services.roadmap_service import generate_roadmap, recalculate_roadmap_milestone_statuses, get_next_action
from ai.provider import LLMProvider
from ai.onboarding import extract_goal_from_text
from models.roadmap import LearnerGoal, Roadmap, RoadmapMilestone, MilestoneItem
from models.skill import Skill, LearnerSkill
from models.resource import Resource
from models.activity import LearningActivity
from recommendation.skill_gap import calculate_system_confidence
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import selectinload, joinedload
from datetime import datetime

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
        existing_ls_ids = {ls.skill_id for ls in db.query(LearnerSkill).filter(LearnerSkill.learner_id == learner_id).all()}
        for skill_name in known_skills:
            if skill_name in skill_map:
                sk_id = skill_map[skill_name].id
                if sk_id not in existing_ls_ids:
                    ls = LearnerSkill(
                        learner_id=learner_id,
                        skill_id=sk_id,
                        self_reported_level=75.0,
                        system_confidence=calculate_system_confidence(75.0, None)
                    )
                    db.add(ls)
                    existing_ls_ids.add(sk_id)
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
    existing_ls_ids = {ls.skill_id for ls in db.query(LearnerSkill).filter(LearnerSkill.learner_id == learner_id).all()}
    for skill_name in req.known_skills:
        if skill_name in skill_map:
            sk_id = skill_map[skill_name].id
            if sk_id not in existing_ls_ids:
                ls = LearnerSkill(
                    learner_id=learner_id,
                    skill_id=sk_id,
                    self_reported_level=75.0,
                    system_confidence=calculate_system_confidence(75.0, None)
                )
                db.add(ls)
                existing_ls_ids.add(sk_id)
    db.commit()
    
    return {
        "status": "success",
        "goal_id": goal.id,
        "title": goal.title,
        "target_role": goal.target_role,
        "timeline_months": goal.timeline_months
    }

class ActionPayload(BaseModel):
    extra: Optional[dict] = None

@router.get("/{learner_id}/next-action")
def learner_next_action(learner_id: int, db: Session = Depends(get_db)):
    return get_next_action(db, learner_id)

@router.post("/{learner_id}/roadmap")
def create_learner_roadmap(learner_id: int, payload: Optional[ActionPayload] = None, db: Session = Depends(get_db)):
    roadmap = generate_roadmap(db, learner_id)
    if not roadmap:
        raise HTTPException(status_code=400, detail="Could not generate roadmap")
    return {
        "status": "success",
        "roadmap_id": roadmap.id,
        "learner_id": learner_id,
        "message": "Roadmap generated successfully"
    }

@router.get("/{learner_id}/roadmap", response_model=RoadmapResponse)
def get_learner_roadmap(learner_id: int, db: Session = Depends(get_db)):
    roadmap = db.query(Roadmap).filter(
        Roadmap.learner_id == learner_id, 
        Roadmap.status.in_(["active", "completed"])
    ).order_by(Roadmap.created_at.desc()).first()
    
    if not roadmap:
        raise HTTPException(status_code=404, detail="No active roadmap found")
        
    recalculate_roadmap_milestone_statuses(db, roadmap.id)
    
    loaded_roadmap = db.query(Roadmap).options(
        selectinload(Roadmap.milestones).selectinload(RoadmapMilestone.items).joinedload(MilestoneItem.resource),
        selectinload(Roadmap.milestones).selectinload(RoadmapMilestone.items).joinedload(MilestoneItem.project)
    ).filter(Roadmap.id == roadmap.id).first()
    
    return RoadmapResponse.model_validate(loaded_roadmap)

@router.post("/{learner_id}/roadmap/milestones/{milestone_id}/start")
def start_milestone_endpoint(learner_id: int, milestone_id: int, payload: Optional[ActionPayload] = None, db: Session = Depends(get_db)):
    roadmap = db.query(Roadmap).filter(
        Roadmap.learner_id == learner_id, 
        Roadmap.status.in_(["active", "completed"])
    ).order_by(Roadmap.created_at.desc()).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="No active roadmap found for learner")
        
    milestone = db.query(RoadmapMilestone).filter(
        RoadmapMilestone.id == milestone_id,
        RoadmapMilestone.roadmap_id == roadmap.id
    ).first()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found in active roadmap")
        
    if milestone.status == "locked":
        raise HTTPException(status_code=400, detail="Cannot start a locked milestone. Complete prerequisite milestones first.")
        
    if milestone.status == "available":
        milestone.status = "in_progress"
        items = db.query(MilestoneItem).filter(MilestoneItem.milestone_id == milestone.id).all()
        if not items:
            resources = db.query(Resource).all()
            top_resources = [r for r in resources if any(s in (r.skill_ids or []) for s in (milestone.skill_ids or []))][:3]
            for res in top_resources:
                db.add(MilestoneItem(milestone_id=milestone.id, resource_id=res.id, item_type="resource", status="not_started"))
            db.add(MilestoneItem(milestone_id=milestone.id, item_type="assessment", status="not_started"))
            db.flush()
            items = db.query(MilestoneItem).filter(MilestoneItem.milestone_id == milestone.id).all()
            
        for it in items:
            if it.status == "not_started":
                it.status = "in_progress"
                break
        db.commit()
        db.refresh(milestone)
        
    return {
        "status": "success",
        "milestone_id": milestone.id,
        "milestone_status": milestone.status,
        "message": f"Milestone '{milestone.title}' is now in progress"
    }

@router.post("/{learner_id}/roadmap/items/{item_id}/complete")
def complete_item_endpoint(learner_id: int, item_id: int, payload: Optional[ActionPayload] = None, db: Session = Depends(get_db)):
    roadmap = db.query(Roadmap).filter(
        Roadmap.learner_id == learner_id, 
        Roadmap.status.in_(["active", "completed"])
    ).order_by(Roadmap.created_at.desc()).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="No active roadmap found")
        
    item = db.query(MilestoneItem).filter(MilestoneItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    milestone = db.query(RoadmapMilestone).filter(
        RoadmapMilestone.id == item.milestone_id,
        RoadmapMilestone.roadmap_id == roadmap.id
    ).first()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found in active roadmap")

    if milestone.status == "locked":
        raise HTTPException(status_code=400, detail="Cannot complete tasks in a locked milestone. Complete prerequisite milestones first.")
        
    item.status = "completed"
    item.completed_at = datetime.utcnow()
    
    if milestone.status == "available":
        milestone.status = "in_progress"
        
    if item.resource_id:
        res = db.query(Resource).filter(Resource.id == item.resource_id).first()
        if res and res.skill_ids:
            for sid in res.skill_ids:
                ls = db.query(LearnerSkill).filter(
                    LearnerSkill.learner_id == learner_id,
                    LearnerSkill.skill_id == sid
                ).first()
                if ls:
                    ls.system_confidence = min(95.0, (ls.system_confidence or 0.0) + 30.0)
                    ls.demonstrated_level = min(95.0, (ls.demonstrated_level or 0.0) + 30.0)

    item_title = item.resource.title if item.resource else f"{item.item_type.capitalize()} Task"
    activity = LearningActivity(
        learner_id=learner_id,
        resource_id=item.resource_id,
        activity_type=f"{item.item_type}_completed",
        description=f"Completed task: {item_title}",
        duration_minutes=int((item.resource.duration_hours or 1) * 60) if item.resource else 30,
        created_at=datetime.utcnow()
    )
    db.add(activity)
    db.commit()
    
    recalculate_roadmap_milestone_statuses(db, roadmap.id)
    
    db.refresh(item)
    db.refresh(milestone)
    return {
        "status": "success", 
        "item_id": item.id, 
        "item_status": item.status,
        "milestone_id": milestone.id,
        "milestone_status": milestone.status
    }
