from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON
from datetime import datetime
from database import Base

class LearningActivity(Base):
    __tablename__ = "learning_activities"

    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learners.id"))
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=True)
    activity_type = Column(String)
    description = Column(String, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learners.id"))
    role = Column(String) # user/assistant
    content = Column(String)
    intent = Column(String, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learners.id"))
    resource_id = Column(Integer, ForeignKey("resources.id"))
    score = Column(Float)
    score_breakdown = Column(JSON, default=dict)
    explanation = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
