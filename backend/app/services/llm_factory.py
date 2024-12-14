from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ai_config import LLMConfig
from app.services.llm_service import LLMService
from app.services.ai_config import AIConfigService

class LLMFactory:
    """Factory for creating LLM service instances"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.config_service = AIConfigService(db)

    async def create_service(
        self,
        config_id: Optional[str] = None
    ) -> LLMService:
        """Create an LLM service instance"""
        try:
            if config_id:
                config = await self.config_service.get_llm_config(config_id)
            else:
                config = await self.config_service.get_active_llm_config()

            return LLMService(config)

        except Exception as e:
            raise ValueError(f"Error creating LLM service: {str(e)}")

    async def create_default_service(self) -> LLLMService:
        """Create an LLM service with default configuration"""
        config = await self.config_service.get_active_llm_config()
        return LLMService(config)

    @staticmethod
    def validate_config(config: LLMConfig) -> bool:
        """Validate LLM configuration"""
        required_fields = ['provider', 'api_key', 'model_name']
        
        for field in required_fields:
            if not getattr(config, field):
                return False

        if config.provider == 'custom' and not config.endpoint_url:
            return False

        return True