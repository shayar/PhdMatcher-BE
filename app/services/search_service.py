import time
from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.professor import professor as crud_professor
from app.services.embedding_service import EmbeddingService
from app.utils.vector_db import VectorDatabase
from app.schemas.search import SearchFilters, SearchResult
from app.schemas.professor import Professor

class SearchService:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = EmbeddingService()
        self.vector_db = VectorDatabase()
    
    def search(
        self,
        query: Optional[str] = None,
        filters: Optional[SearchFilters] = None,
        limit: int = 50,
        offset: int = 0
    ) -> SearchResult:
        """Search professors using query and filters"""
        start_time = time.time()
        
        if query:
            # Semantic search using embeddings
            professors = self._semantic_search(query, filters, limit, offset)
        else:
            # Filter-only search
            professors = self._filter_search(filters, limit, offset)
        
        query_time = (time.time() - start_time) * 1000
        
        return SearchResult(
            professors=professors,
            total_count=len(professors),
            query_time_ms=query_time
        )
    
    def _semantic_search(
        self,
        query: str,
        filters: Optional[SearchFilters],
        limit: int,
        offset: int
    ) -> List[Professor]:
        """Perform semantic search using embeddings"""
        # Generate query embedding
        query_embedding = self.embedding_service.encode_text(query)
        
        # Search similar professors
        similar_professors = self.vector_db.search_similar(
            query_embedding, top_k=limit * 2  # Get more for filtering
        )
        
        if not similar_professors:
            return []
        
        # Get professor IDs and scores
        professor_ids = [prof_id for prof_id, _ in similar_professors]
        similarity_scores = {prof_id: score for prof_id, score in similar_professors}
        
        # Apply filters and get detailed data
        professors = crud_professor.get_filtered_professors(
            self.db,
            professor_ids=professor_ids,
            filters=filters,
            skip=offset,
            limit=limit
        )
        
        # Add similarity scores
        for prof in professors:
            prof.match_score = similarity_scores.get(prof.openalex_id, 0.0)
        
        # Sort by similarity
        professors.sort(key=lambda x: x.match_score or 0, reverse=True)
        
        return professors
    
    def _filter_search(
        self,
        filters: Optional[SearchFilters],
        limit: int,
        offset: int
    ) -> List[Professor]:
        """Perform filter-only search"""
        return crud_professor.get_filtered_professors(
            self.db,
            filters=filters,
            skip=offset,
            limit=limit
        )
