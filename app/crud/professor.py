from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from app.crud.base import CRUDBase
from app.models.professor import Professor
from app.models.institution import Institution
from app.schemas.professor import ProfessorCreate, Professor as ProfessorSchema
from app.schemas.search import SearchFilters

class CRUDProfessor(CRUDBase[Professor, ProfessorCreate, ProfessorCreate]):
    def get_by_openalex_id(self, db: Session, *, openalex_id: str) -> Optional[Professor]:
        return db.query(Professor).filter(Professor.openalex_id == openalex_id).first()

    def get_filtered_professors(
        self,
        db: Session,
        *,
        professor_ids: Optional[List[str]] = None,
        filters: Optional[SearchFilters] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ProfessorSchema]:
        query = db.query(Professor).options(joinedload(Professor.institution))
        
        # Filter by specific professor IDs if provided
        if professor_ids:
            query = query.filter(Professor.openalex_id.in_(professor_ids))
        
        # Apply filters
        if filters:
            if filters.university:
                query = query.join(Institution).filter(
                    Institution.name.ilike(f"%{filters.university}%")
                )
            
            if filters.country:
                query = query.join(Institution).filter(
                    Institution.country.ilike(f"%{filters.country}%")
                )
            
            if filters.city:
                query = query.join(Institution).filter(
                    Institution.city.ilike(f"%{filters.city}%")
                )
            
            if filters.min_works_count:
                query = query.filter(Professor.works_count >= filters.min_works_count)
            
            if filters.min_citations:
                query = query.filter(Professor.cited_by_count >= filters.min_citations)
            
            if filters.concepts:
                # Filter by research concepts (simplified)
                concept_conditions = []
                for concept in filters.concepts:
                    concept_conditions.append(
                        Professor.concepts.op('::text').ilike(f'%{concept}%')
                    )
                if concept_conditions:
                    query = query.filter(or_(*concept_conditions))
        
        professors = query.offset(skip).limit(limit).all()
        
        # Convert to schema with institution name
        result = []
        for prof in professors:
            prof_dict = prof.__dict__.copy()
            prof_dict['institution_name'] = prof.institution.name if prof.institution else None
            result.append(ProfessorSchema(**prof_dict))
        
        return result

    def search_by_concepts(
        self, 
        db: Session, 
        concepts: List[str], 
        limit: int = 100
    ) -> List[Professor]:
        """Search professors by research concepts"""
        concept_conditions = []
        for concept in concepts:
            concept_conditions.append(
                Professor.concepts.op('::text').ilike(f'%{concept}%')
            )
        
        if not concept_conditions:
            return []
        
        return db.query(Professor).filter(
            or_(*concept_conditions)
        ).limit(limit).all()

professor = CRUDProfessor(Professor)