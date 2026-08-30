from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.resource import Resource

router = APIRouter()

@router.get("")
def list_resources(db: Session = Depends(get_db), type: str = None, difficulty: str = None):
    query = db.query(Resource)
    if type:
        query = query.filter(Resource.type == type)
    if difficulty:
        query = query.filter(Resource.difficulty == difficulty)
        
    return query.all()
