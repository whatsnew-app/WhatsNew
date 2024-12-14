from typing import Optional, Dict
from PIL import Image
from io import BytesIO
import numpy as np
from fastapi import HTTPException
import httpx

class ImageProcessor:
    """Handles image processing and optimization"""

    async def process_image(
        self,
        image_url: str,
        target_size: Optional[tuple] = None,
        optimize: bool = True
    ) -> BytesIO:
        """Process and optimize image"""
        try:
            # Fetch image
            image_data = await self._fetch_image(image_url)
            
            # Open image
            image = Image.open(BytesIO(image_data))
            
            # Resize if needed
            if target_size:
                image = self._resize_image(image, target_size)
            
            # Optimize
            if optimize:
                image = self._optimize_image(image)
            
            # Save to buffer
            buffer = BytesIO()
            image.save(buffer, format="PNG", optimize=True)
            buffer.seek(0)
            
            return buffer

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Image processing failed: {str(e)}"
            )

    async def _fetch_image(self, url: str) -> bytes:
        """Fetch image from URL"""
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to fetch image"
                )
            return response.content

    def _resize_image(
        self,
        image: Image.Image,
        target_size: tuple
    ) -> Image.Image:
        """Resize image maintaining aspect ratio"""
        target_width, target_height = target_size
        
        # Calculate aspect ratios
        target_ratio = target_width / target_height
        image_ratio = image.width / image.height
        
        if target_ratio > image_ratio:
            # Width is limiting factor
            new_width = target_width
            new_height = int(new_width / image_ratio)
        else:
            # Height is limiting factor
            new_height = target_height
            new_width = int(new_height * image_ratio)
        
        # Resize
        resized = image.resize((new_width, new_height), Image.LANCZOS)
        
        # Create new image with padding if needed
        if (new_width, new_height) != target_size:
            padded = Image.new("RGB", target_size, (255, 255, 255))
            # Center the image
            left = (target_width - new_width) // 2
            top = (target_height - new_height) // 2
            padded.paste(resized, (left, top))
            return padded
        
        return resized

    def _optimize_image(self, image: Image.Image) -> Image.Image:
        """Optimize image for web delivery"""
        # Convert to RGB if needed
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        
        # Perform basic optimization
        image = image.copy()  # Create a copy to avoid modifying original
        
        # Apply subtle sharpening
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.2)
        
        return image