from sqlalchemy.orm import Session, selectinload, joinedload
from typing import Optional
from models.roadmap import Roadmap, RoadmapMilestone, MilestoneItem
from models.skill import LearnerSkill
from models.resource import Resource
from models.assessment import AssessmentAttempt, Assessment
from models.activity import LearningActivity
from models.learner import Learner
from datetime import datetime

def get_progress(db: Session, learner_id: int, goal_id: Optional[int] = None):
    """Calculate comprehensive progress data for a learner with semantic timeline growth."""
    learner = db.query(Learner).filter(Learner.id == learner_id).first()

    # Find active goal
    from models.roadmap import LearnerGoal, GoalSkillRequirement
    if goal_id:
        active_goal = db.query(LearnerGoal).filter(
            LearnerGoal.id == goal_id,
            LearnerGoal.learner_id == learner_id
        ).first()
    else:
        active_goal = db.query(LearnerGoal).filter(
            LearnerGoal.learner_id == learner_id,
            LearnerGoal.status == "active"
        ).order_by(LearnerGoal.id.desc()).first()

    # Find latest roadmap for active goal (active or completed)
    roadmap_filter = [Roadmap.learner_id == learner_id, Roadmap.status.in_(["active", "completed"])]
    if active_goal:
        roadmap_filter.append(Roadmap.goal_id == active_goal.id)

    roadmap = db.query(Roadmap).options(
        selectinload(Roadmap.milestones).selectinload(RoadmapMilestone.items).joinedload(MilestoneItem.resource)
    ).filter(*roadmap_filter).order_by(Roadmap.created_at.desc()).first()
    
    milestones = []
    milestones_total = 0
    milestones_completed = 0
    
    if roadmap and roadmap.milestones:
        milestones = roadmap.milestones
        milestones_total = len(milestones)
        milestones_completed = sum(1 for m in milestones if m.status == "completed")
        
    overall_progress = (milestones_completed / max(1, milestones_total)) * 100 if milestones_total > 0 else 0
    if milestones_total > 0 and milestones_completed == milestones_total:
        overall_progress = 100.0
    
    # Calculate skill distribution & categorized lists (scoped to active goal's requirements if present)
    goal_skill_ids = None
    if active_goal:
        reqs = db.query(GoalSkillRequirement).filter(GoalSkillRequirement.goal_id == active_goal.id).all()
        if reqs:
            goal_skill_ids = {r.skill_id for r in reqs}

    all_learner_skills = db.query(LearnerSkill).filter(LearnerSkill.learner_id == learner_id).all()
    if goal_skill_ids:
        skills = [s for s in all_learner_skills if s.skill_id in goal_skill_ids]
    else:
        skills = all_learner_skills
    all_skills_map = {s.skill_id: s for s in skills}
    
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
    total_completed_items_count = 0
    if roadmap and roadmap.milestones:
        for m in roadmap.milestones:
            for item in (m.items or []):
                if item.status == "completed":
                    total_completed_items_count += 1
                    if item.resource and item.resource.duration_hours:
                        total_learning_hours += item.resource.duration_hours
    
    # Assessment history
    assessments = db.query(AssessmentAttempt).filter(
        AssessmentAttempt.learner_id == learner_id
    ).order_by(AssessmentAttempt.completed_at.desc()).all()
    assessments_taken = len(assessments)
    average_score = sum(a.score for a in assessments) / max(1, assessments_taken) if assessments_taken > 0 else 0
    
    # Compute mastery metrics
    initial_confidences = [s.self_reported_level for s in skills if s.self_reported_level is not None]
    baseline_mastery = round(sum(initial_confidences) / len(initial_confidences), 1) if initial_confidences else 0.0
    
    current_confidences = [s.system_confidence for s in skills if s.system_confidence is not None]
    current_mastery = round(sum(current_confidences) / len(current_confidences), 1) if current_confidences else baseline_mastery
    mastery_growth = round(current_mastery - baseline_mastery, 1)

    # Active milestone determination
    current_milestone_title = None
    if milestones:
        for m in milestones:
            if m.status in ["in_progress", "available"]:
                current_milestone_title = m.title
                break
        if not current_milestone_title and milestones_completed == milestones_total:
            current_milestone_title = "All Milestones Completed"

    # Velocity status
    if overall_progress >= 50 or (assessments_taken >= 2 and average_score >= 80):
        velocity_status = "Accelerating"
        velocity_badge = "High Velocity"
    elif overall_progress > 0 or total_completed_items_count > 0 or assessments_taken >= 1:
        velocity_status = "Steady Growth"
        velocity_badge = "Active Pace"
    else:
        velocity_status = "Getting Started"
        velocity_badge = "Baseline Set"

    # Build semantic progression timeline
    progression_timeline = []
    
    # Point 0: Baseline
    progression_timeline.append({
        "id": "start",
        "label": "Start",
        "title": "Onboarding Baseline",
        "order_index": -1,
        "status": "completed",
        "progress": 0.0,
        "target_progress": 0.0,
        "mastery": baseline_mastery,
        "assessment_score": None,
        "completed_items": 0,
        "total_items": 0,
        "estimated_hours": 0.0,
        "date": learner.created_at.strftime("%b %d") if learner and learner.created_at else "Start",
        "is_current": milestones_total == 0
    })

    # Milestone points
    cum_completed_milestones = 0
    active_marked = False
    
    for idx, m in enumerate(milestones):
        items_list = m.items or []
        m_total_items = len(items_list)
        m_done_items = sum(1 for it in items_list if it.status == "completed")
        
        if m.status == "completed":
            m_fraction = 1.0
            cum_completed_milestones += 1
        elif m.status == "in_progress" and m_total_items > 0:
            m_fraction = m_done_items / m_total_items
        else:
            m_fraction = 0.0
            
        target_pct = round(((idx + 1) / max(1, milestones_total)) * 100, 1)
        
        if milestones_total > 0:
            cum_prog = round(((cum_completed_milestones + (m_fraction if m.status == "in_progress" else 0)) / milestones_total) * 100, 1)
        else:
            cum_prog = 0.0
            
        m_skill_ids = m.skill_ids or []
        m_confs = [all_skills_map[sid].system_confidence for sid in m_skill_ids if sid in all_skills_map and all_skills_map[sid].system_confidence is not None]
        m_mastery = round(sum(m_confs) / len(m_confs), 1) if m_confs else current_mastery
        
        # Check if assessment score exists for this milestone
        m_assessment_score = None
        for a in assessments:
            if a.assessment_id:
                asst = db.query(Assessment).filter(Assessment.id == a.assessment_id).first()
                if asst and asst.milestone_id == m.id:
                    m_assessment_score = round(a.score, 1)
                    break
        
        is_curr = False
        if not active_marked and m.status in ["in_progress", "available"]:
            is_curr = True
            active_marked = True
        elif not active_marked and idx == milestones_total - 1 and milestones_completed == milestones_total:
            is_curr = True
            active_marked = True

        progression_timeline.append({
            "id": f"m_{m.id}",
            "label": f"M{idx+1}",
            "title": m.title,
            "order_index": idx,
            "status": m.status,
            "progress": cum_prog,
            "target_progress": target_pct,
            "mastery": m_mastery,
            "assessment_score": m_assessment_score,
            "completed_items": m_done_items,
            "total_items": m_total_items,
            "estimated_hours": m.estimated_hours or 0.0,
            "date": m.created_at.strftime("%b %d") if m.created_at else f"Step {idx+1}",
            "is_current": is_curr
        })

    # Recent activity
    recent_activity = []
    activities = db.query(LearningActivity).filter(
        LearningActivity.learner_id == learner_id
    ).order_by(LearningActivity.created_at.desc()).limit(10).all()
    
    for act in activities:
        recent_activity.append({
            "type": act.activity_type or "general",
            "description": act.description,
            "date": act.created_at.isoformat() if act.created_at else ""
        })
        
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
    
    # Chronological assessment scores
    assessment_history = [
        {
            "id": a.id,
            "score": round(a.score, 1),
            "date": a.completed_at.strftime("%b %d") if a.completed_at else "Recent",
            "skill_scores": a.skill_scores or {}
        }
        for a in sorted(assessments, key=lambda x: x.completed_at or datetime.min)
    ]

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
        "current_mastery": current_mastery,
        "baseline_mastery": baseline_mastery,
        "mastery_growth": mastery_growth,
        "velocity_status": velocity_status,
        "velocity_badge": velocity_badge,
        "current_milestone_title": current_milestone_title,
        "progression_timeline": progression_timeline,
        "assessment_history": assessment_history,
        "skill_growth": [],
        "recent_activity": recent_activity
    }
