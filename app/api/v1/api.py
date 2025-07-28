from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, professors, search, matching

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(professors.router, prefix="/professors", tags=["professors"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(matching.router, prefix="/matching", tags=["matching"])