from sqlalchemy.orm import Session
from models.assessment import AssessmentAttempt
from models.roadmap import Roadmap, RoadmapMilestone, MilestoneItem
from models.resource import Resource
from .skill_service import update_learner_skill

def adapt_after_assessment(db: Session, learner_id: int, attempt: AssessmentAttempt):
    """Adapt the learning roadmap based on assessment performance."""
    score = attempt.score
    
    # 1. Update skill demonstrated levels
    for skill_id_str, skill_score in attempt.skill_scores.items():
        update_learner_skill(db, learner_id, int(skill_id_str), demonstrated_level=skill_score)
        
    # 2. Get current roadmap and milestones
    roadmap = db.query(Roadmap).filter(Roadmap.learner_id == learner_id, Roadmap.status == "active").first()
    if not roadmap:
        return {"actions": [], "score": score}
        
    milestones = db.query(RoadmapMilestone).filter(
        RoadmapMilestone.roadmap_id == roadmap.id
    ).order_by(RoadmapMilestone.order_index).all()
    
    actions = []
    
    # Find the milestone this assessment belongs to
    assessment_milestone = None
    if attempt.assessment_id:
        from models.assessment import Assessment
        assessment = db.query(Assessment).filter(Assessment.id == attempt.assessment_id).first()
        if assessment and assessment.milestone_id:
            assessment_milestone = db.query(RoadmapMilestone).filter(
                RoadmapMilestone.id == assessment.milestone_id
            ).first()
    
    # If we can't find the specific milestone, use the current active one
    if not assessment_milestone:
        for m in milestones:
            if m.status in ["available", "in_progress"]:
                assessment_milestone = m
                break
    
    # 3. Apply adaptation rules based on score
    if score < 50:
        # POOR PERFORMANCE: Mark for review, add remediation
        if assessment_milestone:
            assessment_milestone.status = "in_progress"  # Keep it open for review
            actions.append(f"Milestone '{assessment_milestone.title}' requires review — score was {score:.0f}%")
            
            # Find weak skills from this assessment
            weak_skills = [int(sid) for sid, sc in attempt.skill_scores.items() if sc < 50]
            if weak_skills:
                # Add practice resources for weak skills
                resources = db.query(Resource).filter(
                    Resource.difficulty == "beginner"
                ).all()
                practice_resources = [r for r in resources if any(sid in r.skill_ids for sid in weak_skills)]
                added = 0
                for res in practice_resources[:2]:
                    existing = db.query(MilestoneItem).filter(
                        MilestoneItem.milestone_id == assessment_milestone.id,
                        MilestoneItem.resource_id == res.id
                    ).first()
                    if not existing:
                        item = MilestoneItem(
                            milestone_id=assessment_milestone.id,
                            resource_id=res.id,
                            item_type="resource",
                            status="not_started"
                        )
                        db.add(item)
                        added += 1
                if added:
                    actions.append(f"Added {added} remediation resource(s) for weak areas")
            
            # Delay dependent milestones
            actions.append("Delayed dependent milestones until fundamentals are strengthened")
            
    elif score < 70:
        # MODERATE: Mark current milestone as needing more practice
        if assessment_milestone:
            assessment_milestone.status = "in_progress"
            actions.append(f"Continue practicing — score of {score:.0f}% shows good progress but needs reinforcement")
            
            # Add targeted practice for moderate skills
            moderate_skills = [int(sid) for sid, sc in attempt.skill_scores.items() if sc < 70]
            if moderate_skills:
                resources = db.query(Resource).filter(
                    Resource.difficulty == "intermediate"
                ).all()
                practice_resources = [r for r in resources if any(sid in r.skill_ids for sid in moderate_skills)]
                added = 0
                for res in practice_resources[:1]:
                    existing = db.query(MilestoneItem).filter(
                        MilestoneItem.milestone_id == assessment_milestone.id,
                        MilestoneItem.resource_id == res.id
                    ).first()
                    if not existing:
                        item = MilestoneItem(
                            milestone_id=assessment_milestone.id,
                            resource_id=res.id,
                            item_type="resource",
                            status="not_started"
                        )
                        db.add(item)
                        added += 1
                if added:
                    actions.append(f"Added {added} practice resource(s) for skill reinforcement")
                    
    else:
        # STRONG PERFORMANCE (>= 70): Complete milestone, unlock next
        if assessment_milestone:
            assessment_milestone.status = "completed"
            actions.append(f"🎉 Milestone '{assessment_milestone.title}' completed with {score:.0f}%!")
            
            # Mark all items in this milestone as completed
            items = db.query(MilestoneItem).filter(
                MilestoneItem.milestone_id == assessment_milestone.id
            ).all()
            for item in items:
                item.status = "completed"
            
            # Unlock the next milestone
            for m in milestones:
                if m.status == "locked" and m.order_index == assessment_milestone.order_index + 1:
                    m.status = "available"
                    actions.append(f"Unlocked next milestone: '{m.title}'")
                    break
        
        if score >= 90:
            actions.append("Outstanding performance! Consider accelerating through familiar topics")
        
    db.commit()
    return {"actions": actions, "score": score}
