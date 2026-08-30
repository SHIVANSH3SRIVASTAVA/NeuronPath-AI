from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime

class ChatRequest(BaseModel):
    content: str

class ChatResponse(BaseModel):
    content: str
    intent: Optional[str] = None
    action_taken: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None

class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    intent: Optional[str]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ChatHistoryResponse(BaseModel):
    messages: List[ChatMessageResponse]
