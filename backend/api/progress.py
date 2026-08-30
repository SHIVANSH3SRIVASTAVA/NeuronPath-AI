from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from services.progress_service import get_progress as get_progress_data

router = APIRouter()

@router.get("")
def get_progress(learner_id: int, db: Session = Depends(get_db)):
    return get_progress_data(db, learner_id)
