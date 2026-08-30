from sqlalchemy import Column, Integer, String, Float, JSON
from database import Base

class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    type = Column(String) # course/article/video/documentation/project/practice
    provider = Column(String)
    url = Column(String, nullable=True)
    difficulty = Column(String) # beginner/intermediate/advanced
    duration_hours = Column(Float)
    quality_score = Column(Float, default=50.0)
    description = Column(String)
    skill_ids = Column(JSON, default=list)
    prerequisite_skill_ids = Column(JSON, default=list)

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    difficulty = Column(String)
    skill_ids = Column(JSON, default=list)
    estimated_hours = Column(Float)
