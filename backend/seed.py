"""
Comprehensive seed data for NeuronPath.
Seeds skills, prerequisites, resources, and projects across 50+ diverse domains.
"""
from sqlalchemy.orm import Session
from database import engine, Base
from models.skill import Skill, SkillPrerequisite
from models.resource import Resource, Project
from catalog import CATALOG_SKILLS, CATALOG_PREREQUISITES
from catalog_resources import CATALOG_RESOURCES
import logging

logger = logging.getLogger(__name__)

PROJECTS_DATA = [
    {
        "title": "Automated ETL Data Pipeline",
        "difficulty": "intermediate",
        "estimated_hours": 15,
        "description": "Design and build an automated ETL pipeline that ingests, cleans, and stores analytical datasets.",
        "skills": ["SQL Fundamentals", "Python Basics", "Data Cleaning"],
        "deliverables": "Working Python script with SQLite database and automated tests"
    },
    {
        "title": "Full-Stack Task & Portfolio Dashboard",
        "difficulty": "intermediate",
        "estimated_hours": 20,
        "description": "Build a responsive full-stack application with user authentication, REST APIs, and database persistence.",
        "skills": ["JavaScript Essentials", "RESTful API Design", "Git & Version Control"],
        "deliverables": "Full-stack web application with responsive UI and API documentation"
    },
    {
        "title": "Containerized Microservice Deployment",
        "difficulty": "intermediate",
        "estimated_hours": 12,
        "description": "Containerize a multi-service application with Docker Compose and set up CI/CD automation.",
        "skills": ["Docker Basics", "Linux Command Line", "CI/CD Pipelines"],
        "deliverables": "Dockerfile, docker-compose.yml, and automated GitHub Actions workflow"
    },
    {
        "title": "End-to-End ML Predictive Model",
        "difficulty": "advanced",
        "estimated_hours": 25,
        "description": "Build, evaluate, and deploy a machine learning model with REST API endpoints and metric tracking.",
        "skills": ["Python Basics", "ML Fundamentals", "Model Deployment & MLOps"],
        "deliverables": "Trained ML model, evaluation report, and containerized FastAPI service"
    }
]

def seed_database(db: Session, force: bool = False):
    """Seed the database with all catalog skills, prerequisites, resources, and project templates."""
    if force:
        logger.info("Force flag set. Dropping and recreating all tables...")
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    logger.info("Syncing database with comprehensive catalog...")

    # 1. Sync Skills
    existing_skills = {s.name: s for s in db.query(Skill).all()}
    skill_map = dict(existing_skills)
    
    for sd in CATALOG_SKILLS:
        if sd["name"] not in skill_map:
            skill = Skill(**sd)
            db.add(skill)
            db.flush()
            skill_map[skill.name] = skill
        else:
            skill_obj = skill_map[sd["name"]]
            skill_obj.category = sd.get("category", skill_obj.category)
            skill_obj.description = sd.get("description", skill_obj.description)
    db.commit()

    # 2. Sync Prerequisites
    existing_prereqs = set((p.skill_id, p.prerequisite_id) for p in db.query(SkillPrerequisite).all())
    for skill_name, prereq_name, strength in CATALOG_PREREQUISITES:
        if skill_name in skill_map and prereq_name in skill_map:
            s_id = skill_map[skill_name].id
            p_id = skill_map[prereq_name].id
            if (s_id, p_id) not in existing_prereqs:
                prereq = SkillPrerequisite(
                    skill_id=s_id,
                    prerequisite_id=p_id,
                    strength=strength
                )
                db.add(prereq)
                existing_prereqs.add((s_id, p_id))
    db.commit()

    # 3. Sync Resources with explicit skill mappings
    for rd in CATALOG_RESOURCES:
        skill_names = rd.get("skills", [])
        skill_ids = [skill_map[s].id for s in skill_names if s in skill_map]
        
        res = db.query(Resource).filter(Resource.title == rd["title"]).first()
        if not res:
            resource_data = {k: v for k, v in rd.items() if k not in ("skills", "prereq_skills")}
            resource = Resource(
                **resource_data,
                skill_ids=skill_ids,
                prerequisite_skill_ids=[]
            )
            db.add(resource)
        else:
            res.skill_ids = skill_ids
            res.type = rd.get("type", res.type)
            res.provider = rd.get("provider", res.provider)
            res.url = rd.get("url", res.url)
            res.description = rd.get("description", res.description)
            res.quality_score = rd.get("quality_score", res.quality_score)
            res.duration_hours = rd.get("duration_hours", res.duration_hours)
    db.commit()

    # 4. Sync Projects
    existing_projects = {p.title for p in db.query(Project).all()}
    for pd_item in PROJECTS_DATA:
        if pd_item["title"] not in existing_projects:
            skill_names = pd_item.get("skills", [])
            skill_ids = [skill_map[s].id for s in skill_names if s in skill_map]
            project_data = {k: v for k, v in pd_item.items() if k not in ("skills", "deliverables")}
            project = Project(**project_data, skill_ids=skill_ids)
            db.add(project)
            existing_projects.add(pd_item["title"])
    db.commit()

    logger.info("Database catalog seeding completed successfully (no demo accounts created).")
