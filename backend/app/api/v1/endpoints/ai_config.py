from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.api.deps import get_current_superuser, get_db
from app.models.user import User
from app.services.ai_config import AIConfigService
from app.schemas.ai_config import (
    LLMConfig, ImageConfig,
    LLMConfigCreate, ImageConfigCreate,
    ConfigUpdate
)

router = APIRouter()

@router.get("/llm", response_model=List[LLMConfig])
async def get_llm_configs(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser)
):
    service = AIConfigService(db)
    return await service.get_llm_configs()

@router.post("/llm", response_model=LLMConfig)
async def create_llm_config(
    *,
    db: AsyncSession = Depends(get_db),
    config_in: LLMConfigCreate,
    current_user: User = Depends(get_current_superuser)
):
    service = AIConfigService(db)
    return await service.create_llm_config(config_in, current_user.id)

@router.get("/image", response_model=List[ImageConfig])
async def get_image_configs(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser)
):
    service = AIConfigService(db)
    return await service.get_image_configs()

@router.post("/image", response_model=ImageConfig)
async def create_image_config(
    *,
    db: AsyncSession = Depends(get_db),
    config_in: ImageConfigCreate,
    current_user: User = Depends(get_current_superuser)
):
    service = AIConfigService(db)
    return await service.create_image_config(config_in, current_user.id)

@router.put("/llm/{config_id}/set-default")
async def set_default_llm(
    config_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    service = AIConfigService(db)
    await service.set_default_llm(config_id, current_user.id)
    return {"message": "Default LLM configuration updated"}

@router.put("/image/{config_id}/set-default")
async def set_default_image(
    config_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    service = AIConfigService(db)
    await service.set_default_image(config_id, current_user.id)
    return {"message": "Default image configuration updated"}