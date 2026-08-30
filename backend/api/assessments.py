from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.assessment import AssessmentResponse, AssessmentAttemptRequest, AssessmentAttemptResponse
from services.assessment_service import generate_assessment, submit_assessment
from models.assessment import Assessment
from typing import Optional, List
from pydantic import BaseModel

router = APIRouter()

class AssessmentGenerateRequest(BaseModel):
    milestone_id: Optional[int] = None
    skill_ids: Optional[List[int]] = None

@router.post("/generate", response_model=AssessmentResponse)
def create_assessment(learner_id: int, req: Optional[AssessmentGenerateRequest] = None, db: Session = Depends(get_db)):
    mid = req.milestone_id if req else None
    sids = req.skill_ids if req else None
    return generate_assessment(db, learner_id, mid, sids)

@router.get("/{assessment_id}", response_model=AssessmentResponse)
def get_assessment(assessment_id: int, db: Session = Depends(get_db)):
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment

@router.post("/{assessment_id}/submit")
def submit(assessment_id: int, learner_id: int, req: AssessmentAttemptRequest, db: Session = Depends(get_db)):
    return submit_assessment(db, learner_id, assessment_id, req.answers)
