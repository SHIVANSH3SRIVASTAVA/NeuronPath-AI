from sqlalchemy.orm import Session, selectinload, joinedload
from models.roadmap import Roadmap, RoadmapMilestone, MilestoneItem, LearnerGoal, GoalSkillRequirement
from models.skill import LearnerSkill, SkillPrerequisite, Skill
from models.resource import Resource
from models.learner import Learner
from models.activity import LearningActivity
from recommendation.skill_gap import calculate_skill_gaps
from recommendation.prerequisite import build_prerequisite_graph, get_learning_order
from recommendation.engine import rank_resources
from datetime import datetime
from typing import List, Set, Optional
import math
import re

# Generic stop-words that must never be used on their own for technology matching
GENERIC_STOP_WORDS = {
    "basics", "fundamentals", "core", "programming", "development", "developer",
    "course", "tutorial", "guide", "mastery", "complete", "introduction", "intro",
    "advanced", "intermediate", "beginner", "learn", "deep", "dive", "first",
    "steps", "overview", "principles", "engineering", "architecture", "handbook",
    "design", "management", "testing", "building", "practical", "modern", "feature",
    "features", "methods", "data", "system", "systems", "tools", "foundation", "foundations"
}

def extract_distinctive_skill_tokens(skill_name: str) -> Set[str]:
    """Extract distinct technical tokens from a skill name, ignoring common generic English words."""
    tokens = set(re.findall(r'[a-zA-Z0-9+#]+', skill_name.lower()))
    distinctive = {t for t in tokens if len(t) >= 2 and t not in GENERIC_STOP_WORDS}
    return distinctive

def is_resource_relevant_to_skill(
    resource: Resource,
    target_skill_ids: List[int],
    target_skill_names: List[str],
    all_skills_map: dict
) -> bool:
    """
    Strictly validates whether a resource is genuinely relevant to the milestone's primary skill(s).
    A resource is relevant if and only if:
    1. It directly teaches the milestone's primary skill (skill_ids match).
    2. OR its title/description specifically contains the exact skill name phrase or technical tokens using word boundaries.
    """
    res_skill_ids = set(resource.skill_ids or [])
    target_sids = set(target_skill_ids)
    
    # 1. Exact Skill ID match
    if res_skill_ids.intersection(target_sids):
        return True
        
    # 2. Exact Phrase or Word-Boundary Match
    res_text = f"{resource.title} {resource.description or ''}".lower()
    for sname in target_skill_names:
        sname_lower = sname.lower()
        # Full skill name phrase match (e.g. "feature engineering", "java fundamentals", "python intermediate")
        if re.search(r'\b' + re.escape(sname_lower) + r'\b', res_text):
            return True
            
        distinctive_tokens = extract_distinctive_skill_tokens(sname)
        if len(distinctive_tokens) >= 1:
            # All distinctive technical tokens must match as whole words
            if all(re.search(r'\b' + re.escape(tok) + r'\b', res_text) for tok in distinctive_tokens):
                # Safeguard against "Java" matching "JavaScript"
                if "java" in distinctive_tokens and "javascript" not in distinctive_tokens:
                    if re.search(r'\bjavascript\b', res_text) and not re.search(r'\bjava\b(?!script)', res_text):
                        continue
                return True
                
    return False

def recalculate_roadmap_milestone_statuses(db: Session, roadmap_id: int):
    """
    Ensure strict milestone completion and sequential unlocking:
    1. If all items in a milestone are completed -> milestone is marked completed.
    2. Milestone 0 (order_index=0) is available/in_progress unless completed.
    3. Milestone i (order_index=i) is unlocked (available) if and only if Milestone i-1 is completed.
    4. If previous milestone is NOT completed, Milestone i remains strictly locked.
    5. Boost learner skill confidence and register completion activities.
    """
    roadmap = db.query(Roadmap).filter(Roadmap.id == roadmap_id).first()
    if not roadmap:
        return

    milestones = db.query(RoadmapMilestone).filter(
        RoadmapMilestone.roadmap_id == roadmap_id
    ).order_by(RoadmapMilestone.order_index).all()
    
    for i, m in enumerate(milestones):
        items = db.query(MilestoneItem).filter(MilestoneItem.milestone_id == m.id).all()
        all_items_done = len(items) > 0 and all(it.status == "completed" for it in items)
        
        if all_items_done:
            if m.status != "completed":
                m.status = "completed"
                if m.skill_ids:
                    for sid in m.skill_ids:
                        ls = db.query(LearnerSkill).filter(
                            LearnerSkill.learner_id == roadmap.learner_id,
                            LearnerSkill.skill_id == sid
                        ).first()
                        if ls:
                            ls.system_confidence = max(ls.system_confidence or 0.0, 85.0)
                            ls.demonstrated_level = max(ls.demonstrated_level or 0.0, 85.0)
                            
                existing_act = db.query(LearningActivity).filter(
                    LearningActivity.learner_id == roadmap.learner_id,
                    LearningActivity.activity_type == "milestone_completed",
                    LearningActivity.description == f"Completed milestone: {m.title}"
                ).first()
                if not existing_act:
                    db.add(LearningActivity(
                        learner_id=roadmap.learner_id,
                        activity_type="milestone_completed",
                        description=f"Completed milestone: {m.title}",
                        created_at=datetime.utcnow()
                    ))
        elif m.status == "completed":
            has_started = any(it.status in ["in_progress", "completed"] for it in items)
            m.status = "in_progress" if has_started else "available"

        # Sequential locking / unlocking logic
        if i == 0:
            if m.status == "locked":
                m.status = "available"
        else:
            prev_m = milestones[i - 1]
            if prev_m.status == "completed":
                if m.status == "locked":
                    m.status = "available"
            else:
                if not all_items_done:
                    m.status = "locked"

    # Check if entire roadmap is completed
    all_milestones_done = len(milestones) > 0 and all(m.status == "completed" for m in milestones)
    if all_milestones_done:
        roadmap.status = "completed"
        existing_act = db.query(LearningActivity).filter(
            LearningActivity.learner_id == roadmap.learner_id,
            LearningActivity.activity_type == "roadmap_completed"
        ).first()
        if not existing_act:
            db.add(LearningActivity(
                learner_id=roadmap.learner_id,
                activity_type="roadmap_completed",
                description=f"Mastered entire roadmap track for {roadmap.goal.target_role if roadmap.goal else 'target role'}! 🎉",
                created_at=datetime.utcnow()
            ))
    elif roadmap.status == "completed":
        roadmap.status = "active"

    db.commit()

def generate_roadmap(db: Session, learner_id: int):
    """
    Dynamically decomposes the learner's goal into a fine-grained, coherent milestone graph.
    Each milestone attaches strictly relevant learning resources teaching its primary skill.
    """
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    goal = db.query(LearnerGoal).filter(
        LearnerGoal.learner_id == learner_id, 
        LearnerGoal.status.in_(["active", "completed"])
    ).first()
    
    if not goal:
        return None
        
    requirements = db.query(GoalSkillRequirement).filter(GoalSkillRequirement.goal_id == goal.id).all()
    req_skill_ids = [r.skill_id for r in requirements]
    skill_weights = {r.skill_id: r.weight for r in requirements}
    
    prereqs = db.query(SkillPrerequisite).all()
    graph = build_prerequisite_graph(prereqs)
    
    learner_skills = db.query(LearnerSkill).filter(LearnerSkill.learner_id == learner_id).all()
    gaps = calculate_skill_gaps(learner_skills, requirements, graph)
    
    # Priority-weighted topological learning order
    order = get_learning_order(req_skill_ids, learner_skills, graph, skill_weights)
    
    old_roadmaps = db.query(Roadmap).filter(
        Roadmap.learner_id == learner_id, 
        Roadmap.status.in_(["active", "completed"])
    ).all()
    for old_r in old_roadmaps:
        old_r.status = "superseded"
        
    roadmap = Roadmap(learner_id=learner_id, goal_id=goal.id)
    db.add(roadmap)
    db.flush()
    
    resources = db.query(Resource).all()
    all_skills_objs = {s.id: s for s in db.query(Skill).all()}
    all_skills = {s.id: s.name for s in all_skills_objs.values()}
    
    # Pre-rank resources once using multi-factor recommendation engine
    ranked = rank_resources(resources, learner, gaps, graph, learner_skills)
    
    milestone_index = 0
    assigned_resource_ids_in_roadmap = set()
    chunk_size = 1 if len(order) <= 18 else 2
    
    milestone_objs = []
    milestone_resources = []
    
    for i in range(0, len(order), chunk_size):
        chunk = order[i:i+chunk_size]
        if not chunk:
            continue
            
        skill_names = [all_skills.get(sid, "") for sid in chunk]
        
        # Format clean, goal-relevant milestone title & topic-specific objective
        if len(skill_names) == 1:
            title = f"{skill_names[0]}"
            skill_obj = all_skills_objs.get(chunk[0])
            topic_desc = skill_obj.description if (skill_obj and skill_obj.description) else f"core concepts and practical techniques of {skill_names[0]}"
            objective = f"Master {topic_desc} for {goal.target_role}"
        elif len(skill_names) == 2:
            title = f"{skill_names[0]} & {skill_names[1]}"
            objective = f"Master {skill_names[0]} and {skill_names[1]} for {goal.target_role}"
        else:
            title = f"{skill_names[0]} & More"
            objective = f"Master {', '.join(skill_names)} for {goal.target_role}"
            
        direct_matches = []
        for r_tuple in ranked:
            res = r_tuple[0]
            if is_resource_relevant_to_skill(res, chunk, skill_names, all_skills):
                # Ensure primary skill match is ranked higher than general match
                res_skill_set = set(res.skill_ids or [])
                is_primary = bool(res_skill_set.intersection(set(chunk)))
                direct_matches.append((res, 1 if is_primary else 0, r_tuple[1]))
                
        # Sort by primary match first, then recommendation score
        direct_matches.sort(key=lambda x: (x[1], x[2]), reverse=True)
        
        # Prioritize unused resources in this roadmap to guarantee distinct learning tasks per milestone
        unused_matches = [item[0] for item in direct_matches if item[0].id not in assigned_resource_ids_in_roadmap]
        used_matches = [item[0] for item in direct_matches if item[0].id in assigned_resource_ids_in_roadmap]
        top_resources = (unused_matches + used_matches)[:3]
        
        # Fallback ONLY to other resources in database that explicitly match the skill name
        if not top_resources:
            for res in resources:
                if is_resource_relevant_to_skill(res, chunk, skill_names, all_skills):
                    if res not in top_resources:
                        top_resources.append(res)
                if len(top_resources) >= 2:
                    break
        
        assigned_resource_ids_in_roadmap.update(r.id for r in top_resources)
        estimated_hours = max(float(sum(r.duration_hours or 0 for r in top_resources)), 6.0)
        
        m_obj = RoadmapMilestone(
            roadmap_id=roadmap.id,
            order_index=milestone_index,
            title=title,
            objective=objective,
            status="available" if milestone_index == 0 else "locked",
            estimated_hours=estimated_hours,
            skill_ids=chunk,
            completion_criteria=f"Complete {title} learning modules and pass the milestone assessment"
        )
        milestone_objs.append(m_obj)
        milestone_resources.append(top_resources)
        milestone_index += 1
        
    db.add_all(milestone_objs)
    db.flush()
    
    item_objs = []
    for m_obj, top_resources in zip(milestone_objs, milestone_resources):
        for res in top_resources:
            item_objs.append(MilestoneItem(
                milestone_id=m_obj.id,
                resource_id=res.id,
                item_type="resource",
                status="not_started"
            ))
        item_objs.append(MilestoneItem(
            milestone_id=m_obj.id,
            item_type="assessment",
            status="not_started"
        ))
        
    db.add_all(item_objs)
    db.commit()
    
    return db.query(Roadmap).options(
        selectinload(Roadmap.milestones).selectinload(RoadmapMilestone.items).joinedload(MilestoneItem.resource),
        selectinload(Roadmap.milestones).selectinload(RoadmapMilestone.items).joinedload(MilestoneItem.project)
    ).filter(Roadmap.id == roadmap.id).first()

def get_next_action(db: Session, learner_id: int):
    roadmap = db.query(Roadmap).filter(
        Roadmap.learner_id == learner_id, 
        Roadmap.status.in_(["active", "completed"])
    ).order_by(Roadmap.created_at.desc()).first()
    
    if not roadmap:
        goal = db.query(LearnerGoal).filter(
            LearnerGoal.learner_id == learner_id, 
            LearnerGoal.status.in_(["active", "completed"])
        ).first()
        if not goal:
            return {
                "action": "create_goal", 
                "title": "Set Your Goal",
                "description": "Describe your target career role to generate your adaptive path.",
                "message": "You need to set a goal first."
            }
        return {
            "action": "create_goal", 
            "title": "Build Your Roadmap",
            "description": "Ready to create your personalized step-by-step roadmap.",
            "message": "Build your roadmap to start learning."
        }
        
    milestones = db.query(RoadmapMilestone).filter(
        RoadmapMilestone.roadmap_id == roadmap.id
    ).order_by(RoadmapMilestone.order_index).all()
    
    for m in milestones:
        if m.status in ["available", "in_progress"]:
            items = db.query(MilestoneItem).filter(
                MilestoneItem.milestone_id == m.id, 
                MilestoneItem.status != "completed"
            ).all()
            if items:
                next_item = items[0]
                if next_item.item_type == "assessment":
                    return {
                        "action": "take_assessment", 
                        "milestone_id": m.id, 
                        "title": f"Take Assessment: {m.title}",
                        "description": f"Validate your progress with an adaptive assessment for '{m.title}'.",
                        "message": f"Take the assessment for '{m.title}'"
                    }
                elif next_item.item_type == "resource":
                    res = db.query(Resource).filter(Resource.id == next_item.resource_id).first()
                    return {
                        "action": "start_resource", 
                        "resource_id": res.id if res else None, 
                        "milestone_id": m.id,
                        "title": res.title if res else "Next Module", 
                        "description": f"Continue learning '{res.title if res else 'next module'}' in {m.title}.",
                        "message": f"Start learning: {res.title if res else 'next module'}"
                    }
    
    all_milestones_done = len(milestones) > 0 and all(m.status == "completed" for m in milestones)
    if all_milestones_done or roadmap.status == "completed":
        return {
            "action": "all_completed", 
            "title": "Roadmap Track Completed! 🎉",
            "description": "You have completed all milestones and tasks in this personalized learning roadmap.",
            "message": "You have completed your roadmap!"
        }
        
    return {
        "action": "start_resource", 
        "description": "Continue your learning path.",
        "message": "Continue your learning path."
    }
