from typing import Optional, List
from pydantic import BaseModel

class SearchFilters(BaseModel):
    university: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    concepts: Optional[List[str]] = None
    min_works_count: Optional[int] = None
    min_citations: Optional[int] = None

class SearchQuery(BaseModel):
    query: Optional[str] = None
    filters: Optional[SearchFilters] = None
    limit: Optional[int] = 50
    offset: Optional[int] = 0

class SearchResult(BaseModel):
    professors: List[Professor]
    total_count: int
    query_time_ms: float

class MatchRequest(BaseModel):
    user_id: int
    filters: Optional[SearchFilters] = None
    top_k: Optional[int] = 50

class MatchResult(BaseModel):
    user_id: int
    matches: List[Professor]
    total_matches: int
    processing_time_ms: float