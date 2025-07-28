import json
import time
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from app.utils.vector_db import VectorDatabase
from app.services.embedding_service import EmbeddingService
from app.crud.professor import professor as crud_professor
from app.crud.user import user as crud_user
from app.schemas.professor import Professor
from app.schemas.search import SearchFilters, MatchResult
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class MatchingService:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = EmbeddingService()
        self.vector_db = VectorDatabase()
    
    def find_matches(
        self, 
        user_id: int, 
        filters: Optional[SearchFilters] = None,
        top_k: int = 50
    ) -> MatchResult:
        """Find matching professors for a user"""
        start_time = time.time()
        
        # Get user and their embedding
        user = crud_user.get(self.db, id=user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        user_embedding = self._get_user_embedding(user)
        if not user_embedding:
            raise ValueError("User embedding not available")
        
        # Search for similar professors
        similar_professors = self.vector_db.search_similar(
            user_embedding, top_k=top_k * 2  # Get more for filtering
        )
        
        # Apply filters and get detailed professor data
        filtered_matches = self._apply_filters_and_get_details(
            similar_professors, filters, top_k
        )
        
        # Generate match explanations
        matches_with_explanations = [
            self._add_match_explanation(prof, user) 
            for prof in filtered_matches
        ]
        
        processing_time = (time.time() - start_time) * 1000
        
        return MatchResult(
            user_id=user_id,
            matches=matches_with_explanations,
            total_matches=len(matches_with_explanations),
            processing_time_ms=processing_time
        )
    
    def _get_user_embedding(self, user) -> Optional[List[float]]:
        """Get or generate user embedding"""
        if user.resume_embedding:
            return json.loads(user.resume_embedding)
        
        # Generate embedding from profile and resume text
        text_parts = []
        
        if user.resume_text:
            text_parts.append(user.resume_text)
        
        if user.research_interests:
            text_parts.append(" ".join(user.research_interests))
        
        if user.field_of_study:
            text_parts.append(user.field_of_study)
        
        if not text_parts:
            return None
        
        combined_text = " ".join(text_parts)
        embedding = self.embedding_service.encode_text(combined_text)
        
        # Save embedding to user record
        user.resume_embedding = json.dumps(embedding)
        self.db.commit()
        
        return embedding
    
    def _apply_filters_and_get_details(
        self, 
        similar_professors: List[Tuple[str, float]], 
        filters: Optional[SearchFilters],
        top_k: int
    ) -> List[Professor]:
        """Apply filters and get detailed professor information"""
        professor_ids = [prof_id for prof_id, _ in similar_professors]
        similarity_scores = {prof_id: score for prof_id, score in similar_professors}
        
        # Get professors from database with filters
        professors = crud_professor.get_filtered_professors(
            self.db, 
            professor_ids=professor_ids,
            filters=filters,
            limit=top_k
        )
        
        # Add similarity scores
        for prof in professors:
            prof.match_score = similarity_scores.get(prof.openalex_id, 0.0)
        
        # Sort by similarity score
        professors.sort(key=lambda x: x.match_score, reverse=True)
        
        return professors[:top_k]
    
    def _add_match_explanation(self, professor: Professor, user) -> Professor:
        """Add explanation for why this professor matches the user"""
        explanation = {
            "similarity_score": professor.match_score,
            "matching_concepts": [],
            "common_keywords": []
        }
        
        # Find matching research concepts
        if user.research_interests and professor.concepts:
            user_interests = [interest.lower() for interest in user.research_interests]
            prof_concepts = [concept["display_name"].lower() for concept in professor.concepts]
            
            common_concepts = list(set(user_interests) & set(prof_concepts))
            explanation["matching_concepts"] = common_concepts
        
        # Add keyword matching from resume
        if user.resume_text and professor.research_summary:
            explanation["common_keywords"] = self._find_common_keywords(
                user.resume_text, professor.research_summary
            )
        
        professor.match_explanation = explanation
        return professor
    
    def _find_common_keywords(self, text1: str, text2: str) -> List[str]:
        """Find common important keywords between two texts"""
        # Simple keyword extraction (in production, use more sophisticated NLP)
        import re
        from collections import Counter
        
        # Extract words (simple approach)
        words1 = set(re.findall(r'\b[a-z]{4,}\b', text1.lower()))
        words2 = set(re.findall(r'\b[a-z]{4,}\b', text2.lower()))
        
        common = list(words1 & words2)
        return common[:10]  # Return top 10 common keywords