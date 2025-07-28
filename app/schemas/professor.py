from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class ConceptScore(BaseModel):
    id: str
    display_name: str
    level: int
    score: float

class ProfessorBase(BaseModel):
    openalex_id: str
    name: str
    display_name: Optional[str] = None
    institution_id: Optional[str] = None
    works_count: Optional[int] = 0
    cited_by_count: Optional[int] = 0
    h_index: Optional[int] = 0
    i10_index: Optional[int] = 0
    concepts: Optional[List[ConceptScore]] = None
    research_summary: Optional[str] = None
    orcid: Optional[str] = None
    homepage_url: Optional[str] = None

class Professor(ProfessorBase):
    institution_name: Optional[str] = None
    match_score: Optional[float] = None
    match_explanation: Optional[Dict[str, Any]] = None
    
    class Config:
        orm_mode = True

class ProfessorCreate(ProfessorBase):
    embedding: Optional[List[float]] = None

class ProfessorInDB(ProfessorBase):
    embedding: Optional[List[float]] = None
    last_updated: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True