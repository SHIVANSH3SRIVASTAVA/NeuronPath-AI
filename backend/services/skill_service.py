from sqlalchemy.orm import Session
from models.skill import LearnerSkill, Skill, SkillPrerequisite
from recommendation.skill_gap import calculate_system_confidence

def update_learner_skill(db: Session, learner_id: int, skill_id: int, self_reported_level: float = None, demonstrated_level: float = None):
    ls = db.query(LearnerSkill).filter(
        LearnerSkill.learner_id == learner_id,
        LearnerSkill.skill_id == skill_id
    ).first()
    
    if not ls:
        ls = LearnerSkill(learner_id=learner_id, skill_id=skill_id)
        db.add(ls)
        
    if self_reported_level is not None:
        ls.self_reported_level = self_reported_level
    if demonstrated_level is not None:
        ls.demonstrated_level = demonstrated_level
        
    ls.system_confidence = calculate_system_confidence(ls.self_reported_level, ls.demonstrated_level)
    
    db.commit()
    db.refresh(ls)
    return ls

def get_learner_skills(db: Session, learner_id: int):
    return db.query(LearnerSkill).filter(LearnerSkill.learner_id == learner_id).all()
