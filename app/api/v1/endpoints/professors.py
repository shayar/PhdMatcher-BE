from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.core.database import get_db
from app.crud.professor import professor as crud_professor
from app.schemas.professor import Professor
from app.services.openalex_service import OpenAlexService

router = APIRouter()

@router.get("/", response_model=List[Professor])
def get_professors(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = Query(default=50, le=100),
    university: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    min_works: Optional[int] = Query(None),
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """Get professors with optional filters"""
    from app.schemas.search import SearchFilters
    
    filters = SearchFilters(
        university=university,
        country=country,
        min_works_count=min_works
    )
    
    professors = crud_professor.get_filtered_professors(
        db, filters=filters, skip=skip, limit=limit
    )
    return professors

@router.get("/{professor_id}", response_model=Professor)
def get_professor(
    *,
    db: Session = Depends(get_db),
    professor_id: str,
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """Get professor by OpenAlex ID"""
    professor = crud_professor.get_by_openalex_id(db, openalex_id=professor_id)
    if not professor:
        raise HTTPException(status_code=404, detail="Professor not found")
    
    # Convert to schema
    prof_dict = professor.__dict__.copy()
    prof_dict['institution_name'] = professor.institution.name if professor.institution else None
    return Professor(**prof_dict)

@router.post("/sync")
async def sync_professors(
    *,
    db: Session = Depends(get_db),
    institution_ror: str = Query(..., description="ROR ID of institution to sync"),
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """Sync professors from OpenAlex for a specific institution"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    openalex_service = OpenAlexService(db)
    result = await openalex_service.sync_professors_by_institution(institution_ror)
    
    return {
        "message": f"Synced {result['synced_count']} professors",
        "synced_count": result["synced_count"],
        "updated_count": result["updated_count"]
    }
