from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any, Optional
from datetime import datetime

class AssessmentQuestionResponse(BaseModel):
    id: int
    skill_id: int
    question_text: str
    options: List[str]
    # NOTE: correct_answer_index is omitted to prevent client-side inspection before submission
    difficulty: str
    
    model_config = ConfigDict(from_attributes=True)

class AssessmentResponse(BaseModel):
    id: int
    title: str
    status: str
    questions: List[AssessmentQuestionResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

class AssessmentAttemptRequest(BaseModel):
    answers: Dict[str, Any] # question_id (as str) -> selected_index or option text

class AssessmentAttemptResponse(BaseModel):
    id: int
    assessment_id: int
    score: float
    skill_scores: Dict[str, float]
    completed_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
