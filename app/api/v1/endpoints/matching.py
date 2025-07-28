from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.core.database import get_db
from app.schemas.search import MatchRequest, MatchResult
from app.services.matching_service import MatchingService

router = APIRouter()

@router.post("/", response_model=MatchResult)
def find_matches(
    *,
    db: Session = Depends(get_db),
    match_request: MatchRequest,
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """Find matching professors for current user"""
    # Ensure user can only request matches for themselves (unless superuser)
    if match_request.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    matching_service = MatchingService(db)
    
    try:
        matches = matching_service.find_matches(
            user_id=match_request.user_id,
            filters=match_request.filters,
            top_k=match_request.top_k or 50
        )
        return matches
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me", response_model=MatchResult)
def find_my_matches(
    *,
    db: Session = Depends(get_db),
    top_k: int = 50,
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """Find matches for current user"""
    matching_service = MatchingService(db)
    
    try:
        matches = matching_service.find_matches(
            user_id=current_user.id,
            top_k=top_k
        )
        return matches
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))