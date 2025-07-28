from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.api import deps
from app.core.database import get_db
from app.crud.user import user as crud_user
from app.models.user import User
from app.schemas.user import User as UserSchema, UserUpdate
from app.services.file_service import FileService
from app.services.user_service import UserService

router = APIRouter()

@router.get("/me", response_model=UserSchema)
def read_user_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Get current user"""
    return current_user

@router.put("/me", response_model=UserSchema)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Update current user"""
    user = crud_user.update(db, db_obj=current_user, obj_in=user_in)
    return user

@router.post("/upload-resume")
async def upload_resume(
    *,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Upload user resume"""
    file_service = FileService()
    user_service = UserService(db)
    
    # Validate file
    if not file_service.validate_file(file):
        raise HTTPException(status_code=400, detail="Invalid file type or size")
    
    # Process and upload file
    result = await file_service.upload_resume(file, current_user.id)
    
    # Update user record
    await user_service.update_resume(current_user.id, result)
    
    return {"message": "Resume uploaded successfully", "file_path": result["file_path"]}