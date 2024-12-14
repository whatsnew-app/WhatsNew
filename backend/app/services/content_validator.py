from typing import Dict, List, Optional
import re
from datetime import datetime
from pydantic import BaseModel, validator
from urllib.parse import urlparse

class ContentValidation(BaseModel):
    title: str
    content: str
    summary: str
    image_prompt: str
    source_urls: List[str]
    published_date: datetime

    @validator('title')
    def validate_title(cls, v):
        if len(v) < 10 or len(v) > 200:
            raise ValueError("Title must be between 10 and 200 characters")
        return v

    @validator('content')
    def validate_content(cls, v):
        if len(v) < 100:
            raise ValueError("Content must be at least 100 characters")
        return v

    @validator('summary')
    def validate_summary(cls, v):
        if len(v) < 50 or len(v) > 500:
            raise ValueError("Summary must be between 50 and 500 characters")
        return v

    @validator('source_urls')
    def validate_urls(cls, v):
        for url in v:
            try:
                result = urlparse(url)
                if not all([result.scheme, result.netloc]):
                    raise ValueError(f"Invalid URL: {url}")
            except Exception:
                raise ValueError(f"Invalid URL: {url}")
        return v

class ContentValidator:
    """Validates generated content and source materials"""

    def __init__(self):
        self.min_content_length = 100
        self.max_title_length = 200
        self.banned_patterns = [
            r'(?i)\b(viagra|cialis|casino|porn)\b',
            r'(?i)(click here|buy now|subscribe)',
            r'(?i)(lottery|winner|jackpot)',
        ]

    async def validate_content(
        self,
        content: Dict,
        source_urls: List[str]
    ) -> bool:
        """Validate generated content"""
        try:
            # Create validation model
            validation = ContentValidation(
                title=content['title'],
                content=content['content'],
                summary=content['summary'],
                image_prompt=content['image_prompt'],
                source_urls=source_urls,
                published_date=datetime.utcnow()
            )

            # Check for banned patterns
            text_to_check = f"{content['title']} {content['content']} {content['summary']}"
            if self._contains_banned_patterns(text_to_check):
                raise ValueError("Content contains prohibited patterns")

            # Check content originality
            if not self._check_originality(content['content']):
                raise ValueError("Content appears to be copied")

            return True

        except Exception as e:
            raise ValueError(f"Content validation failed: {str(e)}")

    def _contains_banned_patterns(self, text: str) -> bool:
        """Check for banned patterns in text"""
        for pattern in self.banned_patterns:
            if re.search(pattern, text):
                return True
        return False

    def _check_originality(self, content: str) -> bool:
        """Basic check for content originality"""
        # Implement more sophisticated originality checking if needed
        # This could include:
        # - Similarity checking against source materials
        # - Plagiarism detection
        # - AI content detection
        return True

    @staticmethod
    def sanitize_content(content: str) -> str:
        """Sanitize content for safety"""
        # Remove potential HTML/script tags
        content = re.sub(r'<[^>]+>', '', content)
        
        # Remove multiple spaces
        content = re.sub(r'\s+', ' ', content)
        
        # Remove control characters
        content = ''.join(char for char in content if ord(char) >= 32)
        
        return content.strip()