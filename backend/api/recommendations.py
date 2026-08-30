from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models.learner import Learner
from core.deps import verify_learner_access
from models.roadmap import LearnerGoal, GoalSkillRequirement
from models.skill import Skill, LearnerSkill, SkillPrerequisite
from models.resource import Resource
from recommendation.skill_gap import calculate_skill_gaps
from recommendation.prerequisite import build_prerequisite_graph
from recommendation.engine import rank_resources

router = APIRouter()

@router.get("")
def get_recommendations(learner_id: int, db: Session = Depends(get_db), _access: Optional[Learner] = Depends(verify_learner_access)):
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    goal = db.query(LearnerGoal).filter(LearnerGoal.learner_id == learner_id, LearnerGoal.status == "active").first()
    if not goal:
        return []
        
    requirements = db.query(GoalSkillRequirement).filter(GoalSkillRequirement.goal_id == goal.id).all()
    learner_skills = db.query(LearnerSkill).filter(LearnerSkill.learner_id == learner_id).all()
    prereqs = db.query(SkillPrerequisite).all()
    graph = build_prerequisite_graph(prereqs)
    
    gaps = calculate_skill_gaps(learner_skills, requirements, graph)
    resources = db.query(Resource).all()
    
    ranked = rank_resources(resources, learner, gaps, graph, learner_skills)
    
    skill_lookup = {s.id: s.name for s in db.query(Skill).all()}
    gap_skill_ids = {g.skill_id for g in gaps}
    
    results = []
    for resource, score, breakdown in ranked[:60]:
        res_skills = [skill_lookup.get(sid, f"Skill {sid}") for sid in (resource.skill_ids or []) if sid in gap_skill_ids]
        if res_skills:
            explanation = f"Recommended to master: {', '.join(res_skills[:3])}"
        else:
            explanation = f"Recommended high-quality {resource.type} resource for your learning path"
            
        results.append({
            "resource": resource,
            "score": round(score, 1),
            "score_breakdown": {k: round(v, 3) for k, v in breakdown.items()},
            "explanation": explanation
        })
        
    return results
