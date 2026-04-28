from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

class ContractAnalysis(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    document_name: str
    document_type: str  # "text", "pdf", "image"
    original_text: str
    simplified_text: Optional[str] = None
    key_points: Optional[List[str]] = None
    risks: Optional[List[str]] = None
    legal_terms: Optional[dict] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
