from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models.learner import Learner
from core.deps import verify_learner_access
from schemas.coach import ChatRequest, ChatResponse
from ai.provider import LLMProvider
from ai.coach import process_coach_message, get_chat_history

router = APIRouter()
llm = LLMProvider()

@router.post("/chat", response_model=ChatResponse)
async def chat(learner_id: int, req: ChatRequest, db: Session = Depends(get_db), _access: Optional[Learner] = Depends(verify_learner_access)):
    return await process_coach_message(learner_id, req.content, db, llm)

@router.get("/history")
def history(learner_id: int, db: Session = Depends(get_db), _access: Optional[Learner] = Depends(verify_learner_access)):
    return get_chat_history(db, learner_id)

