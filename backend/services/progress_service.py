from sqlalchemy.orm import Session
from models.roadmap import Roadmap, RoadmapMilestone, MilestoneItem
from models.skill import LearnerSkill
from models.resource import Resource
from models.assessment import AssessmentAttempt
from models.activity import LearningActivity, ChatMessage

def get_progress(db: Session, learner_id: int):
    """Calculate comprehensive progress data for a learner."""
    # Find latest roadmap (active or completed)
    roadmap = db.query(Roadmap).filter(
        Roadmap.learner_id == learner_id, 
        Roadmap.status.in_(["active", "completed"])
    ).order_by(Roadmap.created_at.desc()).first()
    
    milestones = []
    milestones_total = 0
    milestones_completed = 0
    
    if roadmap:
        milestones = db.query(RoadmapMilestone).filter(
            RoadmapMilestone.roadmap_id == roadmap.id
        ).order_by(RoadmapMilestone.order_index).all()
        milestones_total = len(milestones)
        milestones_completed = sum(1 for m in milestones if m.status == "completed")
        
    overall_progress = (milestones_completed / max(1, milestones_total)) * 100 if milestones_total > 0 else 0
    if milestones_total > 0 and milestones_completed == milestones_total:
        overall_progress = 100.0
    
    # Calculate skill distribution & categorized lists
    skills = db.query(LearnerSkill).filter(LearnerSkill.learner_id == learner_id).all()
    
    categorized_skills = {
        "mastered": [],
        "developing": [],
        "weak": [],
        "missing": []
    }
    
    for s in skills:
        conf = s.system_confidence or 0.0
        skill_info = {
            "skill_id": s.skill_id,
            "name": s.skill.name if s.skill else f"Skill #{s.skill_id}",
            "category": s.skill.category if s.skill else "General",
            "proficiency": round(conf, 1),
            "demonstrated": round(s.demonstrated_level, 1) if s.demonstrated_level is not None else None,
            "self_reported": round(s.self_reported_level, 1) if s.self_reported_level is not None else None,
        }
        if conf >= 80:
            categorized_skills["mastered"].append(skill_info)
        elif conf >= 40:
            categorized_skills["developing"].append(skill_info)
        elif conf >= 10:
            categorized_skills["weak"].append(skill_info)
        else:
            categorized_skills["missing"].append(skill_info)
            
    skills_mastered = len(categorized_skills["mastered"])
    skills_developing = len(categorized_skills["developing"])
    skills_weak = len(categorized_skills["weak"])
    skills_missing = len(categorized_skills["missing"])
    
    # Calculate total learning hours from completed resource items
    total_learning_hours = 0
    if roadmap:
        completed_items = db.query(MilestoneItem).join(RoadmapMilestone).filter(
            RoadmapMilestone.roadmap_id == roadmap.id,
            MilestoneItem.status == "completed",
            MilestoneItem.resource_id.isnot(None)
        ).all()
        for item in completed_items:
            res = db.query(Resource).filter(Resource.id == item.resource_id).first()
            if res and res.duration_hours:
                total_learning_hours += res.duration_hours
    
    # Assessment history
    assessments = db.query(AssessmentAttempt).filter(
        AssessmentAttempt.learner_id == learner_id
    ).order_by(AssessmentAttempt.completed_at.desc()).all()
    assessments_taken = len(assessments)
    average_score = sum(a.score for a in assessments) / max(1, assessments_taken) if assessments_taken > 0 else 0
    
    # Recent activity
    recent_activity = []
    
    # 1. Check logged LearningActivity
    activities = db.query(LearningActivity).filter(
        LearningActivity.learner_id == learner_id
    ).order_by(LearningActivity.created_at.desc()).limit(10).all()
    
    for act in activities:
        recent_activity.append({
            "type": act.activity_type or "general",
            "description": act.description,
            "date": act.created_at.isoformat() if act.created_at else ""
        })
        
    # 2. Add assessments and completed milestones if activities are sparse
    if len(recent_activity) < 3:
        for a in assessments[:3]:
            recent_activity.append({
                "type": "assessment",
                "description": f"Scored {a.score:.0f}% on assessment",
                "date": a.completed_at.isoformat() if a.completed_at else ""
            })
        for m in milestones:
            if m.status == "completed":
                desc = f"Completed milestone: {m.title}"
                if not any(r.get("description") == desc for r in recent_activity):
                    recent_activity.append({
                        "type": "milestone",
                        "description": desc,
                        "date": ""
                    })
                    
    recent_activity = recent_activity[:10]
    
    return {
        "overall_progress": round(overall_progress, 1),
        "milestones_completed": milestones_completed,
        "milestones_total": milestones_total,
        "skills_mastered": skills_mastered,
        "skills_developing": skills_developing,
        "skills_weak": skills_weak,
        "skills_missing": skills_missing,
        "categorized_skills": categorized_skills,
        "total_learning_hours": round(total_learning_hours, 1),
        "assessments_taken": assessments_taken,
        "average_score": round(average_score, 1),
        "skill_growth": [],
        "recent_activity": recent_activity
    }
