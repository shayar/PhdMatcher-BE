from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    education_level: Optional[str] = None
    field_of_study: Optional[str] = None
    research_interests: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    target_universities: Optional[List[str]] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: Optional[int] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    resume_file_path: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str