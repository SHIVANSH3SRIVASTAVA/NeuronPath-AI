from sqlalchemy.orm import Session
from models.roadmap import LearnerGoal, GoalSkillRequirement
from models.skill import Skill, LearnerSkill
from catalog import CATALOG_ROLE_PRESETS
import re

def derive_skill_requirements(target_role: str, title: str, all_skills: list) -> list:
    """
    Find the best matching preset from the comprehensive catalog or dynamically
    match skills from the database using keyword analysis.
    """
    target_lower = target_role.lower().strip()
    title_lower = title.lower().strip()
    combined_query = f"{target_lower} {title_lower}"
    
    # 1. Exact match in catalog presets (High priority)
    for preset_name, reqs in CATALOG_ROLE_PRESETS.items():
        if preset_name.lower() == target_lower:
            return reqs
            
    # 2. Match role against domain keywords
    KEYWORD_MAPPINGS = [
        # Programming
        (["python", "django", "fastapi", "flask"], "Python Developer"),
        (["java", "spring", "jvm"], "Java Developer"),
        (["c++", "cpp", "stl"], "C++ Developer"),
        (["c programming", "embedded c", "c language"], "C Developer"),
        (["c#", "csharp", ".net", "dotnet", "asp.net"], "C# & .NET Developer"),
        (["typescript", "ts"], "TypeScript Developer"),
        (["javascript", "js", "ecmascript"], "JavaScript Developer"),
        (["golang", "go language", "go developer"], "Go Developer"),
        (["rust", "cargo"], "Rust Developer"),
        (["kotlin"], "Kotlin Developer"),
        (["swift", "ios"], "Swift Developer"),
        (["r programming", "tidyverse", "r language", "r data"], "R Data Analyst"),
        (["php", "laravel"], "PHP & Laravel Developer"),

        # Data & AI
        (["data engineer", "etl", "spark", "warehousing"], "Data Engineer"),
        (["data analyst", "analytics", "bi analyst"], "Data Analyst"),
        (["data scientist", "data science"], "Data Scientist"),
        (["machine learning", "ml engineer"], "Machine Learning Engineer"),
        (["ai engineer", "prompt engineer", "llm", "rag"], "AI Engineer"),
        (["deep learning", "pytorch", "neural network"], "Deep Learning Specialist"),
        (["nlp", "natural language", "transformers", "text mining"], "NLP Engineer"),
        (["computer vision", "opencv", "cnn", "image recognition"], "Computer Vision Engineer"),
        (["business intelligence", "power bi", "tableau", "dashboard"], "Business Intelligence Developer"),

        # Software / Web / Mobile
        (["full stack", "fullstack", "full-stack", "software developer", "web app"], "Full Stack Developer"),
        (["frontend", "react", "vue", "angular", "css", "html"], "Frontend Developer"),
        (["backend", "api developer", "microservices", "server"], "Backend Developer"),
        (["web developer", "web development"], "Web Developer"),
        (["mobile", "flutter", "dart", "react native"], "Mobile App Developer"),
        (["android"], "Android Developer"),
        (["ios", "swiftui"], "iOS Developer"),
        (["game dev", "unity", "unreal", "game design"], "Game Developer"),
        (["software engineer", "software engineering", "clean code"], "Software Engineer"),
        (["api", "rest api", "graphql"], "API Developer"),

        # Cloud & DevOps
        (["devops", "ci/cd", "continuous integration"], "DevOps Engineer"),
        (["docker", "container", "containers", "containerization"], "Docker & Container Specialist"),
        (["kubernetes", "k8s", "helm"], "Kubernetes Administrator"),
        (["cloud engineer", "cloud architecture"], "Cloud Engineer"),
        (["aws", "amazon web services"], "AWS Cloud Architect"),
        (["azure", "microsoft cloud"], "Microsoft Azure Specialist"),
        (["gcp", "google cloud"], "Google Cloud Engineer"),
        (["sre", "site reliability", "monitoring", "prometheus"], "Site Reliability Engineer (SRE)"),

        # DB / CS / Security
        (["sql developer", "sql database", "relational database"], "SQL Developer"),
        (["dba", "database admin", "database management"], "Database Administrator (DBA)"),
        (["data structures", "algorithms", "dsa", "leetcode"], "Data Structures & Algorithms Specialist"),
        (["system design", "distributed systems", "scalability"], "System Design Architect"),
        (["computer networks", "networking", "tcp/ip", "protocols"], "Computer Networks Engineer"),
        (["operating system", "os", "kernel", "concurrency"], "Operating Systems Engineer"),
        (["cybersecurity", "security", "infosec", "ethical hacking", "soc"], "Cybersecurity Engineer"),

        # Specializations
        (["blockchain", "smart contracts", "solidity"], "Blockchain Developer"),
        (["web3", "dapp", "decentralized"], "Web3 Developer"),
        (["embedded", "microcontroller", "arduino", "stm32"], "Embedded Systems Engineer"),
        (["iot", "internet of things", "mqtt", "sensor"], "IoT Solutions Engineer"),
        (["robotics", "ros", "robot"], "Robotics Engineer"),
        (["qa", "test automation", "testing", "selenium", "playwright"], "QA & Test Automation Engineer"),
        (["ui/ux", "ui design", "ux", "figma", "wireframing"], "UI/UX Designer"),
        (["product manager", "product management", "scrum", "agile"], "Product Manager"),
    ]

    for keywords, role_preset in KEYWORD_MAPPINGS:
        if any(k in target_lower for k in keywords):
            return CATALOG_ROLE_PRESETS.get(role_preset, CATALOG_ROLE_PRESETS["Full Stack Developer"])

    for keywords, role_preset in KEYWORD_MAPPINGS:
        if any(k in combined_query for k in keywords):
            return CATALOG_ROLE_PRESETS.get(role_preset, CATALOG_ROLE_PRESETS["Full Stack Developer"])

    # 3. Substring match in catalog presets
    for preset_name, reqs in CATALOG_ROLE_PRESETS.items():
        p_low = preset_name.lower()
        if p_low in target_lower or target_lower in p_low:
            return reqs

    # 4. Dynamic semantic scoring against all skills in database
    matched = []
    query_words = set(re.findall(r'\w+', combined_query))
    
    for skill in all_skills:
        skill_words = set(re.findall(r'\w+', f"{skill.name} {skill.category} {skill.description}".lower()))
        overlap = len(query_words.intersection(skill_words))
        if overlap > 0:
            matched.append((skill.name, min(95.0, 70.0 + overlap * 10.0), min(1.0, 0.6 + overlap * 0.2)))
            
    if len(matched) >= 3:
        return sorted(matched, key=lambda x: x[2], reverse=True)[:10]
        
    # Default balanced skills foundation
    return [
        ("HTML Fundamentals", 90, 0.9),
        ("JavaScript Fundamentals", 90, 0.9),
        ("Git & Version Control", 80, 0.8),
        ("RESTful API Design", 80, 0.8),
        ("Databases & SQL", 80, 0.8),
    ]

def get_learner_goals(db: Session, learner_id: int):
    """Retrieve all goals for a learner, sorted with active goal first."""
    goals = db.query(LearnerGoal).filter(
        LearnerGoal.learner_id == learner_id
    ).order_by(LearnerGoal.created_at.desc()).all()
    
    # If no goal is active but goals exist, activate the first one
    active = next((g for g in goals if g.status == "active"), None)
    if not active and goals:
        goals[0].status = "active"
        db.commit()
        db.refresh(goals[0])
        
    return sorted(goals, key=lambda g: (0 if g.status == "active" else 1, g.id))

def create_goal(db: Session, learner_id: int, title: str, target_role: str, timeline_months: int, set_active: bool = True):
    """Create a new goal for a learner and attach skill requirements."""
    if set_active:
        existing_goals = db.query(LearnerGoal).filter(
            LearnerGoal.learner_id == learner_id,
            LearnerGoal.status == "active"
        ).all()
        for g in existing_goals:
            g.status = "inactive"
        db.commit()

    goal = LearnerGoal(
        learner_id=learner_id,
        title=title,
        target_role=target_role,
        timeline_months=timeline_months,
        status="active" if set_active else "inactive"
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    
    all_skills = db.query(Skill).all()
    skills_map = {s.name: s for s in all_skills}
    existing_ls_ids = {ls.skill_id for ls in db.query(LearnerSkill).filter(LearnerSkill.learner_id == learner_id).all()}
    
    requirements = derive_skill_requirements(target_role, title, all_skills)
    
    for skill_name, required_prof, weight in requirements:
        if skill_name in skills_map:
            skill_obj = skills_map[skill_name]
            req = GoalSkillRequirement(
                goal_id=goal.id,
                skill_id=skill_obj.id,
                required_proficiency=float(required_prof),
                weight=float(weight)
            )
            db.add(req)
            
            # Ensure LearnerSkill exists for this learner so skill proficiency metrics are always trackable
            if skill_obj.id not in existing_ls_ids:
                ls = LearnerSkill(
                    learner_id=learner_id,
                    skill_id=skill_obj.id,
                    self_reported_level=0.0,
                    system_confidence=0.0
                )
                db.add(ls)
                existing_ls_ids.add(skill_obj.id)
            
    db.commit()
    return goal

def activate_goal(db: Session, learner_id: int, goal_id: int):
    """Switch active goal: set target goal to active and others to inactive."""
    goal = db.query(LearnerGoal).filter(
        LearnerGoal.id == goal_id,
        LearnerGoal.learner_id == learner_id
    ).first()
    if not goal:
        return None
        
    all_goals = db.query(LearnerGoal).filter(
        LearnerGoal.learner_id == learner_id
    ).all()
    for g in all_goals:
        g.status = "active" if g.id == goal_id else "inactive"
        
    db.commit()
    db.refresh(goal)
    return goal

def delete_goal(db: Session, learner_id: int, goal_id: int):
    """
    Safely delete a specific goal and its associated roadmap & milestones.
    Does NOT touch the learner account or other goals.
    If the deleted goal was active, activates another existing goal.
    """
    goal = db.query(LearnerGoal).filter(
        LearnerGoal.id == goal_id,
        LearnerGoal.learner_id == learner_id
    ).first()
    if not goal:
        return None
        
    was_active = (goal.status == "active")
    
    from models.roadmap import Roadmap, RoadmapMilestone, MilestoneItem
    
    # 1. Delete Roadmaps & Milestone Items for this goal
    roadmaps = db.query(Roadmap).filter(
        Roadmap.learner_id == learner_id,
        Roadmap.goal_id == goal_id
    ).all()
    for rm in roadmaps:
        milestones = db.query(RoadmapMilestone).filter(RoadmapMilestone.roadmap_id == rm.id).all()
        for ms in milestones:
            db.query(MilestoneItem).filter(MilestoneItem.milestone_id == ms.id).delete()
        db.query(RoadmapMilestone).filter(RoadmapMilestone.roadmap_id == rm.id).delete()
        db.delete(rm)
        
    # 2. Delete Goal Skill Requirements
    db.query(GoalSkillRequirement).filter(GoalSkillRequirement.goal_id == goal_id).delete()
    
    # 3. Delete the Goal itself
    db.delete(goal)
    db.commit()
    
    # 4. If deleted goal was active, automatically activate the next existing goal
    new_active_goal = None
    remaining_goals = db.query(LearnerGoal).filter(
        LearnerGoal.learner_id == learner_id
    ).order_by(LearnerGoal.created_at.desc()).all()
    
    if was_active and remaining_goals:
        remaining_goals[0].status = "active"
        for other in remaining_goals[1:]:
            other.status = "inactive"
        db.commit()
        db.refresh(remaining_goals[0])
        new_active_goal = remaining_goals[0]
    elif not was_active and remaining_goals:
        new_active_goal = next((g for g in remaining_goals if g.status == "active"), remaining_goals[0])
        
    return {
        "deleted_goal_id": goal_id,
        "active_goal": new_active_goal,
        "remaining_goals": remaining_goals
    }

