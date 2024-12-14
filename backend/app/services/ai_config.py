from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from uuid import UUID

from app.models.ai_config import LLMConfig as LLMConfigModel, ImageConfig as ImageConfigModel
from app.schemas.ai_config import LLMConfigCreate, ImageConfigCreate, ConfigUpdate

class AIConfigService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_active_llm_config(self) -> LLMConfigModel:
        config = await self.db.scalar(
            select(LLMConfigModel)
            .where(LLMConfigModel.is_active == True, LLMConfigModel.is_default == True)
        )
        if not config:
            raise ValueError("No active LLM configuration found")
        return config

    async def get_active_image_config(self) -> ImageConfigModel:
        config = await self.db.scalar(
            select(ImageConfigModel)
            .where(ImageConfigModel.is_active == True, ImageConfigModel.is_default == True)
        )
        if not config:
            raise ValueError("No active image configuration found")
        return config

    async def create_llm_config(
        self, config_in: LLMConfigCreate, user_id: UUID
    ) -> LLMConfigModel:
        config = LLMConfigModel(
            **config_in.dict(),
            created_by=user_id,
            updated_by=user_id
        )
        self.db.add(config)
        await self.db.commit()
        await self.db.refresh(config)
        return config

    async def create_image_config(
        self, config_in: ImageConfigCreate, user_id: UUID
    ) -> ImageConfigModel:
        config = ImageConfigModel(
            **config_in.dict(),
            created_by=user_id,
            updated_by=user_id
        )
        self.db.add(config)
        await self.db.commit()
        await self.db.refresh(config)
        return config

    async def set_default_llm(self, config_id: UUID, user_id: UUID):
        await self.db.execute(
            update(LLMConfigModel)
            .where(LLMConfigModel.is_default == True)
            .values(is_default=False)
        )
        await self.db.execute(
            update(LLMConfigModel)
            .where(LLMConfigModel.id == config_id)
            .values(is_default=True, updated_by=user_id)
        )
        await self.db.commit()

    async def set_default_image(self, config_id: UUID, user_id: UUID):
        await self.db.execute(
            update(ImageConfigModel)
            .where(ImageConfigModel.is_default == True)
            .values(is_default=False)
        )
        await self.db.execute(
            update(ImageConfigModel)
            .where(ImageConfigModel.id == config_id)
            .values(is_default=True, updated_by=user_id)
        )
        await self.db.commit()