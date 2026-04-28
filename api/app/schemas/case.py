from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

class CaseAnalysis(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    case_title: str
    case_type: str  # Civil, Criminal, Family, Property, etc.
    case_description: str
    analysis: Optional[str] = None
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    strategy: Optional[List[str]] = None
    questions_for_lawyer: Optional[List[str]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    case_id: str
    role: str  # "user" or "assistant"
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
