from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON
from datetime import datetime
from database import Base
from sqlalchemy.orm import relationship

class LearnerGoal(Base):
    __tablename__ = "learner_goals"

    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learners.id"))
    title = Column(String)
    target_role = Column(String)
    timeline_months = Column(Integer)
    status = Column(String, default="active") # active/completed/changed
    created_at = Column(DateTime, default=datetime.utcnow)

class GoalSkillRequirement(Base):
    __tablename__ = "goal_skill_requirements"

    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("learner_goals.id"))
    skill_id = Column(Integer, ForeignKey("skills.id"))
    required_proficiency = Column(Float, default=100.0)
    weight = Column(Float, default=1.0)

    skill = relationship("Skill", lazy="joined")

class Roadmap(Base):
    __tablename__ = "roadmaps"

    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learners.id"))
    goal_id = Column(Integer, ForeignKey("learner_goals.id"))
    status = Column(String, default="active") # active/completed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    milestones = relationship("RoadmapMilestone", lazy="joined", order_by="RoadmapMilestone.order_index")
    goal = relationship("LearnerGoal", lazy="joined")

class RoadmapMilestone(Base):
    __tablename__ = "roadmap_milestones"

    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id"))
    order_index = Column(Integer)
    title = Column(String)
    objective = Column(String)
    status = Column(String, default="locked") # locked/available/in_progress/completed
    estimated_hours = Column(Float)
    skill_ids = Column(JSON, default=list)
    completion_criteria = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("MilestoneItem", lazy="joined")

class MilestoneItem(Base):
    __tablename__ = "milestone_items"

    id = Column(Integer, primary_key=True, index=True)
    milestone_id = Column(Integer, ForeignKey("roadmap_milestones.id"))
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    item_type = Column(String) # resource/project/assessment
    status = Column(String, default="not_started") # not_started/in_progress/completed
    completed_at = Column(DateTime, nullable=True)

    resource = relationship("Resource", lazy="joined")
    project = relationship("Project", lazy="joined")
