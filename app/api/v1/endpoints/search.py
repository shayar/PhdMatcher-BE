from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.core.database import get_db
from app.schemas.search import SearchQuery, SearchResult
from app.services.search_service import SearchService

router = APIRouter()

@router.post("/", response_model=SearchResult)
def search_professors(
    *,
    db: Session = Depends(get_db),
    search_query: SearchQuery,
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """Search professors using natural language query and filters"""
    search_service = SearchService(db)
    
    try:
        results = search_service.search(
            query=search_query.query,
            filters=search_query.filters,
            limit=search_query.limit,
            offset=search_query.offset
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))