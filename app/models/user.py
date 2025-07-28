from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, Boolean
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Profile information
    education_level = Column(String)  # Bachelor's, Master's
    field_of_study = Column(String)
    research_interests = Column(JSON)  # List of interests
    preferred_locations = Column(JSON)  # List of preferred locations
    target_universities = Column(JSON)  # List of target universities
    
    # Resume information
    resume_file_path = Column(String)
    resume_text = Column(Text)
    resume_embedding = Column(JSON)  # Stored as JSON array
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())