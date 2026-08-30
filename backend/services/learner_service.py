from sqlalchemy.orm import Session
from models.learner import Learner
from schemas.learner import LearnerCreate, LearnerUpdate

def create_learner(db: Session, learner: LearnerCreate):
    db_learner = Learner(**learner.model_dump())
    db.add(db_learner)
    db.commit()
    db.refresh(db_learner)
    return db_learner

def get_learner(db: Session, learner_id: int):
    return db.query(Learner).filter(Learner.id == learner_id).first()

def update_learner(db: Session, learner_id: int, learner: LearnerUpdate):
    db_learner = get_learner(db, learner_id)
    if not db_learner:
        return None
    for key, value in learner.model_dump(exclude_unset=True).items():
        if value is not None:
            if key == "email":
                value = value.strip().lower()
            setattr(db_learner, key, value)
    db.commit()
    db.refresh(db_learner)
    return db_learner
