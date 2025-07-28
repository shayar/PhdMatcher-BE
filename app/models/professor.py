from sqlalchemy import Column, String, JSON, Float, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Professor(Base):
    __tablename__ = "professors"
    
    openalex_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    display_name = Column(String)
    
    # Institution information
    institution_id = Column(String, ForeignKey("institutions.openalex_id"))
    institution = relationship("Institution", back_populates="professors")
    
    # Profile information
    works_count = Column(Integer, default=0)
    cited_by_count = Column(Integer, default=0)
    h_index = Column(Integer, default=0)
    i10_index = Column(Integer, default=0)
    
    # Research areas (OpenAlex concepts)
    concepts = Column(JSON)  # List of concept objects with scores
    research_summary = Column(Text)
    
    # Contact information (if available)
    orcid = Column(String)
    homepage_url = Column(String)
    
    # Embedding for similarity search
    embedding = Column(JSON)  # Stored as JSON array
    
    # Timestamps
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())