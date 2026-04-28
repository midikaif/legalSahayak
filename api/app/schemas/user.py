from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
import uuid

class UserType(str):
    COMMON = "common"
    LAWYER = "lawyer"

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    password_hash: str
    full_name: str
    user_type: str  # "common" or "lawyer"
    phone: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Lawyer-specific fields
    specialization: Optional[str] = None
    bar_council_number: Optional[str] = None
    years_of_experience: Optional[int] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    rating: Optional[float] = 0.0
    cases_handled: Optional[int] = 0

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    user_type: str
    phone: Optional[str] = None
    specialization: Optional[str] = None
    bar_council_number: Optional[str] = None
    years_of_experience: Optional[int] = None
    location: Optional[str] = None
    bio: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict
