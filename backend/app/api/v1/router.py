from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    news,
    prompts,
    ai_config,
    public
)

api_router = APIRouter()

# Add all routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(public.router, prefix="/public", tags=["Public"])
api_router.include_router(news.router, prefix="/news", tags=["News"])
api_router.include_router(prompts.router, prefix="/prompts", tags=["Prompts"])
api_router.include_router(ai_config.router, prefix="/admin/ai-config", tags=["AI Configuration"])