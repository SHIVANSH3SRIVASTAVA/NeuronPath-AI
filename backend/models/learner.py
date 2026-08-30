from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from datetime import datetime
from database import Base

class Learner(Base):
    __tablename__ = "learners"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=True)
    experience_level = Column(String, default="beginner") # beginner/intermediate/advanced
    weekly_hours = Column(Float, default=10.0)
    learning_style = Column(String, nullable=True)
    preferred_formats = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
