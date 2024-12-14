from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ai_config import ImageConfig
from app.services.image_service import ImageService
from app.services.ai_config import AIConfigService

class ImageFactory:
    """Factory for creating image service instances"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.config_service = AIConfigService(db)

    async def create_service(
        self,
        config_id: Optional[str] = None
    ) -> ImageService:
        """Create an image service instance"""
        try:
            if config_id:
                config = await self.config_service.get_image_config(config_id)
            else:
                config = await self.config_service.get_active_image_config()

            return ImageService(config)

        except Exception as e:
            raise ValueError(f"Error creating image service: {str(e)}")

    async def create_default_service(self) -> ImageService:
        """Create an image service with default configuration"""
        config = await self.config_service.get_active_image_config()
        return ImageService(config)

    @staticmethod
    def validate_config(config: ImageConfig) -> bool:
        """Validate image configuration"""
        required_fields = ['provider', 'api_key', 'model_name']
        
        for field in required_fields:
            if not getattr(config, field):
                return False

        if config.provider in [ImageProvider.CUSTOM, ImageProvider.MIDJOURNEY]:
            if not config.endpoint_url:
                return False

        return True

    @staticmethod
    def get_default_parameters(provider: str) -> Dict:
        """Get default parameters for each provider"""
        defaults = {
            "dalle": {
                "quality": "standard",
                "style": "natural",
                "response_format": "url"
            },
            "stable_diffusion": {
                "cfg_scale": 7,
                "steps": 50,
                "sampler": "K_EULER_ANCESTRAL"
            },
            "midjourney": {
                "quality": "1",
                "style": "raw"
            }
        }
        return defaults.get(provider, {})