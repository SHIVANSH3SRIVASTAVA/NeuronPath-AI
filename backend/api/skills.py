from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models.learner import Learner
from core.deps import verify_learner_access
from schemas.skill import LearnerSkillResponse, LearnerSkillUpdate, SkillGapResponse
from services.skill_service import get_learner_skills, update_learner_skill
from models.roadmap import LearnerGoal, GoalSkillRequirement
from recommendation.skill_gap import calculate_skill_gaps

router = APIRouter()

@router.get("", response_model=list[LearnerSkillResponse])
def get_skills(learner_id: int, goal_id: Optional[int] = None, db: Session = Depends(get_db), _access: Optional[Learner] = Depends(verify_learner_access)):
    if goal_id:
        goal = db.query(LearnerGoal).filter(LearnerGoal.id == goal_id, LearnerGoal.learner_id == learner_id).first()
    else:
        goal = db.query(LearnerGoal).filter(LearnerGoal.learner_id == learner_id, LearnerGoal.status == "active").order_by(LearnerGoal.id.desc()).first()
        
    if goal:
        reqs = db.query(GoalSkillRequirement).filter(GoalSkillRequirement.goal_id == goal.id).all()
        if reqs:
            req_skill_ids = {r.skill_id for r in reqs}
            all_s = get_learner_skills(db, learner_id)
            return [s for s in all_s if s.skill_id in req_skill_ids]
    return get_learner_skills(db, learner_id)

@router.put("/{skill_id}", response_model=LearnerSkillResponse)
def update_skill(learner_id: int, skill_id: int, req: LearnerSkillUpdate, db: Session = Depends(get_db), _access: Optional[Learner] = Depends(verify_learner_access)):
    return update_learner_skill(db, learner_id, skill_id, req.self_reported_level, req.demonstrated_level)

@router.get("/gaps", response_model=list[SkillGapResponse])
def get_skill_gaps(learner_id: int, goal_id: Optional[int] = None, db: Session = Depends(get_db), _access: Optional[Learner] = Depends(verify_learner_access)):
    if goal_id:
        goal = db.query(LearnerGoal).filter(LearnerGoal.id == goal_id, LearnerGoal.learner_id == learner_id).first()
    else:
        goal = db.query(LearnerGoal).filter(LearnerGoal.learner_id == learner_id, LearnerGoal.status == "active").order_by(LearnerGoal.id.desc()).first()
    if not goal:
        return []
        
    requirements = db.query(GoalSkillRequirement).filter(GoalSkillRequirement.goal_id == goal.id).all()
    learner_skills = get_learner_skills(db, learner_id)
    
    gaps = calculate_skill_gaps(learner_skills, requirements, None)
    
    return [
        {
            "skill_id": g.skill_id,
            "skill_name": g.skill_name,
            "current_proficiency": g.current,
            "required_proficiency": g.required,
            "gap": g.gap,
            "priority": g.priority
        } for g in gaps
    ]
