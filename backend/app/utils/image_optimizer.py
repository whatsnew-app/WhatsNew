import io
from PIL import Image, ImageOps
from typing import Tuple, Optional
import numpy as np

class ImageOptimizer:
    """Utility class for image optimization"""

    @staticmethod
    def optimize_for_web(
        image_data: bytes,
        max_size: Tuple[int, int] = (1200, 1200),
        quality: int = 85,
        format: str = "JPEG"
    ) -> bytes:
        """Optimize image for web delivery"""
        img = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if needed
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            img = img.convert('RGB')
        
        # Resize if larger than max_size
        if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
            img.thumbnail(max_size, Image.LANCZOS)
        
        # Apply automatic contrast optimization
        img = ImageOps.autocontrast(img, cutoff=0.5)
        
        # Save optimized image
        output = io.BytesIO()
        img.save(
            output,
            format=format,
            quality=quality,
            optimize=True,
            progressive=True
        )
        
        return output.getvalue()

    @staticmethod
    def create_thumbnail(
        image_data: bytes,
        size: Tuple[int, int],
        crop: bool = True
    ) -> bytes:
        """Create thumbnail from image"""
        img = Image.open(io.BytesIO(image_data))
        
        if crop:
            # Calculate dimensions to maintain aspect ratio
            thumb = ImageOps.fit(img, size, Image.LANCZOS)
        else:
            # Resize maintaining aspect ratio
            img.thumbnail(size, Image.LANCZOS)
            thumb = img
        
        # Save thumbnail
        output = io.BytesIO()
        thumb.save(output, 'JPEG', quality=85, optimize=True)
        return output.getvalue()

    @staticmethod
    def add_watermark(
        image_data: bytes,
        watermark_text: str,
        position: str = 'bottom-right',
        opacity: float = 0.5
    ) -> bytes:
        """Add watermark to image"""
        from PIL import ImageDraw, ImageFont
        
        # Open image
        img = Image.open(io.BytesIO(image_data)).convert('RGB')
        
        # Create transparent overlay
        overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Calculate text size and position
        font_size = int(min(img.size) * 0.05)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        text_size = draw.textsize(watermark_text, font=font)
        
        # Calculate position
        padding = 10
        if position == 'bottom-right':
            position = (img.size[0] - text_size[0] - padding,
                      img.size[1] - text_size[1] - padding)
        elif position == 'bottom-left':
            position = (padding, img.size[1] - text_size[1] - padding)
        elif position == 'top-right':
            position = (img.size[0] - text_size[0] - padding, padding)
        elif position == 'top-left':
            position = (padding, padding)
        elif position == 'center':
            position = ((img.size[0] - text_size[0]) // 2,
                       (img.size[1] - text_size[1]) // 2)
        else:
            raise ValueError("Invalid position specified")

        # Draw watermark text
        draw.text(
            position,
            watermark_text,
            font=font,
            fill=(255, 255, 255, int(255 * opacity))
        )

        # Merge overlay with original image
        watermarked = Image.alpha_composite(img.convert('RGBA'), overlay)
        
        # Convert back to RGB
        watermarked = watermarked.convert('RGB')
        
        # Save result
        output = io.BytesIO()
        watermarked.save(output, 'JPEG', quality=95)
        return output.getvalue()

    @staticmethod
    def compress_image(
        image_data: bytes,
        max_size_kb: int = 500,
        min_quality: int = 60
    ) -> bytes:
        """Compress image to target file size"""
        img = Image.open(io.BytesIO(image_data))
        
        # Initial quality
        quality = 95
        output = io.BytesIO()
        
        while quality >= min_quality:
            output.seek(0)
            output.truncate()
            img.save(output, 'JPEG', quality=quality)
            
            # Check size
            if len(output.getvalue()) <= max_size_kb * 1024:
                break
                
            quality -= 5
        
        if quality < min_quality:
            # If size is still too large, resize the image
            scale_factor = np.sqrt(max_size_kb * 1024 / len(output.getvalue()))
            new_size = tuple(int(dim * scale_factor) for dim in img.size)
            img = img.resize(new_size, Image.LANCZOS)
            
            output = io.BytesIO()
            img.save(output, 'JPEG', quality=min_quality)
        
        return output.getvalue()

    @staticmethod
    def convert_format(
        image_data: bytes,
        target_format: str,
        **kwargs
    ) -> bytes:
        """Convert image to different format"""
        img = Image.open(io.BytesIO(image_data))
        
        # Handle alpha channel for PNG to JPEG conversion
        if target_format.upper() == 'JPEG' and img.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'RGBA':
                background.paste(img, mask=img.split()[3])
            else:
                background.paste(img, mask=img.split()[1])
            img = background
        
        output = io.BytesIO()
        img.save(output, target_format, **kwargs)
        return output.getvalue()

    @staticmethod
    def analyze_image(image_data: bytes) -> dict:
        """Analyze image properties"""
        img = Image.open(io.BytesIO(image_data))
        
        # Calculate average brightness
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        np_img = np.array(img)
        brightness = np.mean(np_img)
        
        # Calculate histogram
        histogram = img.histogram()
        
        return {
            'format': img.format,
            'mode': img.mode,
            'size': img.size,
            'width': img.width,
            'height': img.height,
            'aspect_ratio': round(img.width / img.height, 2),
            'brightness': round(brightness, 2),
            'histogram': histogram,
            'file_size': len(image_data),
            'dpi': img.info.get('dpi', (72, 72))
        }

    @staticmethod
    def auto_enhance(image_data: bytes) -> bytes:
        """Automatically enhance image quality"""
        img = Image.open(io.BytesIO(image_data))
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Auto-contrast
        img = ImageOps.autocontrast(img, cutoff=0.5)
        
        # Sharpen slightly
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.2)
        
        # Adjust color balance
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.1)
        
        # Adjust brightness
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.05)
        
        output = io.BytesIO()
        img.save(output, 'JPEG', quality=95)
        return output.getvalue()