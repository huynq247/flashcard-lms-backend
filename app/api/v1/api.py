"""
API v1 router configuration.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth


api_router = APIRouter()

# Include authentication routes
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Health check for API v1
@api_router.get("/health")
async def health_check():
    """API v1 health check."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "api": "v1"
    }
