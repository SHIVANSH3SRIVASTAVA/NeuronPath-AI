from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas.skill import LearnerSkillResponse, LearnerSkillUpdate, SkillGapResponse
from services.skill_service import get_learner_skills, update_learner_skill
from models.roadmap import LearnerGoal, GoalSkillRequirement
from recommendation.skill_gap import calculate_skill_gaps

router = APIRouter()

@router.get("", response_model=list[LearnerSkillResponse])
def get_skills(learner_id: int, db: Session = Depends(get_db)):
    return get_learner_skills(db, learner_id)

@router.put("/{skill_id}", response_model=LearnerSkillResponse)
def update_skill(learner_id: int, skill_id: int, req: LearnerSkillUpdate, db: Session = Depends(get_db)):
    return update_learner_skill(db, learner_id, skill_id, req.self_reported_level, req.demonstrated_level)

@router.get("/gaps", response_model=list[SkillGapResponse])
def get_skill_gaps(learner_id: int, db: Session = Depends(get_db)):
    goal = db.query(LearnerGoal).filter(LearnerGoal.learner_id == learner_id, LearnerGoal.status == "active").first()
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
