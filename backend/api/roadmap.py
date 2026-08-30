from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.roadmap import RoadmapResponse, NextActionResponse
from services.roadmap_service import generate_roadmap, recalculate_roadmap_milestone_statuses, get_next_action
from models.roadmap import Roadmap, RoadmapMilestone, MilestoneItem
from models.skill import LearnerSkill
from models.resource import Resource
from models.activity import LearningActivity
from datetime import datetime

router = APIRouter()

@router.post("", response_model=RoadmapResponse)
def create_roadmap(learner_id: int, db: Session = Depends(get_db)):
    roadmap = generate_roadmap(db, learner_id)
    if not roadmap:
        raise HTTPException(status_code=400, detail="Could not generate roadmap")
    return roadmap

@router.get("", response_model=RoadmapResponse)
def get_roadmap(learner_id: int, db: Session = Depends(get_db)):
    roadmap = db.query(Roadmap).filter(
        Roadmap.learner_id == learner_id, 
        Roadmap.status.in_(["active", "completed"])
    ).order_by(Roadmap.created_at.desc()).first()
    
    if not roadmap:
        raise HTTPException(status_code=404, detail="No active roadmap found")
        
    # Auto-recalculate statuses to maintain consistent locking/completion
    recalculate_roadmap_milestone_statuses(db, roadmap.id)
    
    milestones = db.query(RoadmapMilestone).filter(
        RoadmapMilestone.roadmap_id == roadmap.id
    ).order_by(RoadmapMilestone.order_index).all()
    roadmap.milestones = milestones
    return roadmap

@router.post("/milestones/{milestone_id}/start")
def start_milestone_endpoint(learner_id: int, milestone_id: int, db: Session = Depends(get_db)):
    """Start an available milestone and update database status to in_progress."""
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
        
    # Update status to in_progress if currently available
    if milestone.status == "available":
        milestone.status = "in_progress"
        # Transition first not_started item to in_progress
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

@router.post("/items/{item_id}/complete")
def complete_item_endpoint(learner_id: int, item_id: int, db: Session = Depends(get_db)):
    """Mark a milestone task item complete, auto-complete parent milestone if all tasks complete, and unlock dependent milestones."""
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

    # Strict server-side validation: reject task completion for locked milestone
    if milestone.status == "locked":
        raise HTTPException(status_code=400, detail="Cannot complete tasks in a locked milestone. Complete prerequisite milestones first.")
        
    item.status = "completed"
    item.completed_at = datetime.utcnow()
    
    if milestone.status == "available":
        milestone.status = "in_progress"
        
    # 1. Boost skill levels for skills linked to this item
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

    # 2. Record learning activity
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
    
    # Recalculate milestone completion & sequential unlock across the roadmap
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

@router.get("/next-action")
def next_action(learner_id: int, db: Session = Depends(get_db)):
    return get_next_action(db, learner_id)
