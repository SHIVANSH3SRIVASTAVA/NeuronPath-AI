from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON
from datetime import datetime
from database import Base
from sqlalchemy.orm import relationship

class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learners.id"))
    milestone_id = Column(Integer, ForeignKey("roadmap_milestones.id"), nullable=True)
    title = Column(String)
    skill_ids = Column(JSON, default=list)
    status = Column(String, default="pending") # pending/completed
    created_at = Column(DateTime, default=datetime.utcnow)

    questions = relationship("AssessmentQuestion", lazy="joined")

class AssessmentQuestion(Base):
    __tablename__ = "assessment_questions"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=True)
    skill_id = Column(Integer, ForeignKey("skills.id"))
    question_text = Column(String)
    options = Column(JSON, default=list)
    correct_answer_index = Column(Integer)
    difficulty = Column(String)
    explanation = Column(String)

class AssessmentAttempt(Base):
    __tablename__ = "assessment_attempts"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"))
    learner_id = Column(Integer, ForeignKey("learners.id"))
    answers = Column(JSON, default=dict)
    score = Column(Float)
    skill_scores = Column(JSON, default=dict)
    completed_at = Column(DateTime, default=datetime.utcnow)
