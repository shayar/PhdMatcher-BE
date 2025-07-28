from sqlalchemy import Column, String, JSON, Integer
from sqlalchemy.orm import relationship
from app.core.database import Base

class Institution(Base):
    __tablename__ = "institutions"
    
    openalex_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    display_name = Column(String)
    
    # Location information
    country_code = Column(String)
    country = Column(String)
    city = Column(String)
    region = Column(String)
    
    # Institution details
    type = Column(String)  # education, company, etc.
    homepage_url = Column(String)
    image_url = Column(String)
    ror_id = Column(String)
    works_count = Column(Integer, default=0)
    
    # Additional metadata
    geo = Column(JSON)  # Latitude, longitude
    
    # Relationships
    professors = relationship("Professor", back_populates="institution")