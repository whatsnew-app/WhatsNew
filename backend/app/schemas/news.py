from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict
from datetime import datetime
from uuid import UUID

class NewsImageBase(BaseModel):
    image_prompt: str
    provider: str
    storage_path: str
    ai_metadata: Optional[Dict] = None

class NewsImageCreate(NewsImageBase):
    news_article_id: UUID

class NewsImage(NewsImageBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class NewsArticleBase(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    source_urls: List[str]
    image_url: Optional[str] = None
    ai_metadata: Optional[Dict] = None
    published_date: datetime

class NewsArticleCreate(NewsArticleBase):
    prompt_id: UUID
    slug: str

class NewsArticleUpdate(NewsArticleBase):
    title: Optional[str] = None
    content: Optional[str] = None
    slug: Optional[str] = None
    summary: Optional[str] = None
    source_urls: Optional[List[str]] = None
    image_url: Optional[str] = None
    ai_metadata: Optional[Dict] = None
    published_date: Optional[datetime] = None

class NewsArticleInDBBase(NewsArticleBase):
    id: UUID
    prompt_id: UUID
    slug: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class NewsArticle(NewsArticleInDBBase):
    pass

class NewsArticleWithPrompt(NewsArticle):
    prompt: "Prompt"  # Forward reference to avoid circular import