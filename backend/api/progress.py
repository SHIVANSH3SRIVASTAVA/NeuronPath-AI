from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models.learner import Learner
from core.deps import verify_learner_access
from services.progress_service import get_progress as get_progress_data

router = APIRouter()

@router.get("")
def get_progress(learner_id: int, goal_id: Optional[int] = None, db: Session = Depends(get_db), _access: Optional[Learner] = Depends(verify_learner_access)):
    return get_progress_data(db, learner_id, goal_id=goal_id)


