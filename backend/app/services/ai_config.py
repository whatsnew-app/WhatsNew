from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from uuid import UUID

from app.models.ai_config import LLMConfig as LLMConfigModel, ImageConfig as ImageConfigModel
from app.schemas.ai_config import LLMConfigCreate, ImageConfigCreate, ConfigUpdate





# app/services/ai_config.py

class AIConfigService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_llm_configs(self) -> List[LLMConfigModel]:
        """Get all LLM configurations"""
        result = await self.db.execute(select(LLMConfigModel))
        return result.scalars().all()

    async def get_llm_config(self, config_id: UUID) -> Optional[LLMConfigModel]:
        """Get a specific LLM configuration by ID"""
        result = await self.db.scalar(
            select(LLMConfigModel).where(LLMConfigModel.id == config_id)
        )
        return result

    async def create_llm_config(self, config_data: LLMConfigCreate, user_id: UUID) -> LLMConfigModel:
        """Create a new LLM configuration"""
        db_config = LLMConfigModel(
            **config_data.dict(),
            created_by=user_id,
            updated_by=user_id  # Add this line
        )
        self.db.add(db_config)
        await self.db.commit()
        await self.db.refresh(db_config)
        return db_config

    async def update_llm_config(
        self, config_id: UUID, config_data: ConfigUpdate
    ) -> Optional[LLMConfigModel]:
        """Update an existing LLM configuration"""
        config = await self.get_llm_config(config_id)
        if not config:
            return None
            
        for key, value in config_data.dict(exclude_unset=True).items():
            setattr(config, key, value)
            
        await self.db.commit()
        await self.db.refresh(config)
        return config

    async def delete_llm_config(self, config_id: UUID) -> bool:
        """Delete an LLM configuration"""
        config = await self.get_llm_config(config_id)
        if not config:
            return False
            
        await self.db.delete(config)
        await self.db.commit()
        return True

    async def set_default_llm(self, config_id: UUID, user_id: UUID) -> Optional[LLMConfigModel]:
        """Set an LLM configuration as default"""
        # First, unset all current defaults
        await self.db.execute(
            update(LLMConfigModel)
            .where(LLMConfigModel.is_default == True)
            .values(is_default=False)
        )
        
        # Then set the new default
        config = await self.get_llm_config(config_id)
        if not config:
            return None
            
        config.is_default = True
        config.updated_by = user_id
        
        await self.db.commit()
        await self.db.refresh(config)
        
        return config

    async def create_image_config(self, config_data: ImageConfigCreate, user_id: UUID) -> ImageConfigModel:
        """Create a new image generation configuration"""
        db_config = ImageConfigModel(
            **config_data.dict(),
            created_by=user_id,
            updated_by=user_id
        )
        self.db.add(db_config)
        await self.db.commit()
        await self.db.refresh(db_config)
        return db_config

    async def get_image_config(self, config_id: UUID) -> Optional[ImageConfigModel]:
        """Get a specific image configuration by ID"""
        result = await self.db.scalar(
            select(ImageConfigModel).where(ImageConfigModel.id == config_id)
        )
        return result

    async def get_image_configs(self) -> List[ImageConfigModel]:
        """Get all image configurations"""
        result = await self.db.execute(select(ImageConfigModel))
        return result.scalars().all()

    async def update_image_config(
        self, config_id: UUID, config_data: ConfigUpdate, user_id: UUID
    ) -> Optional[ImageConfigModel]:
        """Update an existing image configuration"""
        config = await self.get_image_config(config_id)
        if not config:
            return None
            
        for key, value in config_data.dict(exclude_unset=True).items():
            setattr(config, key, value)
        
        config.updated_by = user_id
        await self.db.commit()
        await self.db.refresh(config)
        return config

    async def delete_image_config(self, config_id: UUID) -> bool:
        """Delete an image configuration"""
        config = await self.get_image_config(config_id)
        if not config:
            return False
            
        await self.db.delete(config)
        await self.db.commit()
        return True