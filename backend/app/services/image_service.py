from typing import Dict, Optional, Any
import openai
import httpx
from PIL import Image
from io import BytesIO
import base64
from fastapi import HTTPException
from app.models.ai_config import ImageConfig, ImageProvider
from app.core.config import settings
import os

class ImageService:
    def __init__(self, config: ImageConfig):
        self.config = config
        self._setup_client()

    def _setup_client(self):
        """Initialize the appropriate image generation client"""
        if self.config.provider == ImageProvider.DALLE:
            self.client = openai.Client(api_key=self.config.api_key)
        elif self.config.provider == ImageProvider.STABLE_DIFFUSION:
            self.client = httpx.AsyncClient(
                base_url="https://api.stability.ai",
                headers={"Authorization": f"Bearer {self.config.api_key}"}
            )
        elif self.config.provider == ImageProvider.MIDJOURNEY:
            self.client = httpx.AsyncClient(
                base_url=self.config.endpoint_url,
                headers={"Authorization": f"Bearer {self.config.api_key}"}
            )
        elif self.config.provider == ImageProvider.CUSTOM:
            self.client = httpx.AsyncClient(
                base_url=self.config.endpoint_url,
                headers={"Authorization": f"Bearer {self.config.api_key}"}
            )

    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024"
    ) -> Dict[str, Any]:
        """Generate image using configured provider"""
        try:
            if self.config.provider == ImageProvider.DALLE:
                return await self._generate_dalle(prompt, size)
            elif self.config.provider == ImageProvider.STABLE_DIFFUSION:
                return await self._generate_stable_diffusion(prompt, size)
            elif self.config.provider == ImageProvider.MIDJOURNEY:
                return await self._generate_midjourney(prompt, size)
            elif self.config.provider == ImageProvider.CUSTOM:
                return await self._generate_custom(prompt, size)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Image generation failed: {str(e)}"
            )

    async def _generate_dalle(
        self,
        prompt: str,
        size: str
    ) -> Dict[str, Any]:
        """Generate image using DALL-E"""
        response = await self.client.images.generate(
            model=self.config.model_name,
            prompt=prompt,
            size=size,
            quality=self.config.parameters.get("quality", "standard"),
            n=1
        )

        return {
            "url": response.data[0].url,
            "metadata": {
                "model": self.config.model_name,
                "provider": "dalle",
                "size": size
            }
        }

    async def _generate_stable_diffusion(
        self,
        prompt: str,
        size: str
    ) -> Dict[str, Any]:
        """Generate image using Stable Diffusion"""
        width, height = map(int, size.split('x'))
        
        response = await self.client.post(
            f"/v1/generation/{self.config.model_name}/text-to-image",
            json={
                "text_prompts": [{"text": prompt}],
                "cfg_scale": self.config.parameters.get("cfg_scale", 7),
                "height": height,
                "width": width,
                "samples": 1,
                "steps": self.config.parameters.get("steps", 50)
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Stable Diffusion API error"
            )

        result = response.json()
        image_data = result["artifacts"][0]
        
        # Save the image and get its URL
        image_url = await self._save_image(
            base64.b64decode(image_data["base64"]),
            "stable_diffusion"
        )

        return {
            "url": image_url,
            "metadata": {
                "model": self.config.model_name,
                "provider": "stable_diffusion",
                "size": size
            }
        }

    async def _generate_midjourney(
        self,
        prompt: str,
        size: str
    ) -> Dict[str, Any]:
        """Generate image using Midjourney"""
        response = await self.client.post(
            "/generate",
            json={
                "prompt": prompt,
                "size": size,
                **self.config.parameters
            }
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Midjourney API error"
            )

        result = response.json()
        return {
            "url": result["image_url"],
            "metadata": {
                "model": self.config.model_name,
                "provider": "midjourney",
                "size": size
            }
        }

    async def _generate_custom(
        self,
        prompt: str,
        size: str
    ) -> Dict[str, Any]:
        """Generate image using custom provider"""
        response = await self.client.post(
            "/generate",
            json={
                "prompt": prompt,
                "size": size,
                **self.config.parameters
            }
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Custom provider API error"
            )

        result = response.json()
        return {
            "url": result["image_url"],
            "metadata": {
                "model": self.config.model_name,
                "provider": "custom",
                "size": size
            }
        }

    async def _save_image(
        self,
        image_data: bytes,
        provider: str
    ) -> str:
        """Save image to storage and return URL"""
        # Create directory if it doesn't exist
        save_dir = os.path.join(settings.MEDIA_ROOT, "images", provider)
        os.makedirs(save_dir, exist_ok=True)

        # Generate unique filename
        filename = f"{provider}_{os.urandom(8).hex()}.png"
        filepath = os.path.join(save_dir, filename)

        # Save image
        image = Image.open(BytesIO(image_data))
        image.save(filepath, "PNG")

        # Return URL
        return f"{settings.MEDIA_URL}/images/{provider}/{filename}"

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()