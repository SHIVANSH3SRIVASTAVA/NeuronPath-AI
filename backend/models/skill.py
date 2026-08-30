from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from datetime import datetime
from database import Base
from sqlalchemy.orm import relationship

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    category = Column(String, index=True)
    description = Column(String)

class SkillPrerequisite(Base):
    __tablename__ = "skill_prerequisites"

    id = Column(Integer, primary_key=True, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id"))
    prerequisite_id = Column(Integer, ForeignKey("skills.id"))
    strength = Column(Float, default=1.0)

class LearnerSkill(Base):
    __tablename__ = "learner_skills"

    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learners.id"))
    skill_id = Column(Integer, ForeignKey("skills.id"))
    self_reported_level = Column(Float, default=0.0)
    demonstrated_level = Column(Float, nullable=True)
    system_confidence = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    skill = relationship("Skill", lazy="joined")
