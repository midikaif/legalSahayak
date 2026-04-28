from pydantic import BaseModel, Field
from typing import List
import uuid

class LegalProcedure(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    case_type: str
    title: str
    steps: List[dict]  # [{step_number, description, timeline}]
    required_documents: List[str]
    court_hierarchy: List[str]
    estimated_timeline: str
