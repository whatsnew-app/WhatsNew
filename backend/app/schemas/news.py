# app/schemas/news.py

from datetime import datetime, date
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class NewsArticleBase(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    source_urls: List[str]
    image_url: Optional[str] = None
    ai_metadata: Optional[Dict[str, Any]] = None
    published_date: datetime
    slug: str

class NewsArticleCreate(NewsArticleBase):
    prompt_id: UUID

class NewsArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    source_urls: Optional[List[str]] = None
    image_url: Optional[str] = None
    ai_metadata: Optional[Dict[str, Any]] = None

class NewsArticleInDBBase(NewsArticleBase):
    id: UUID
    prompt_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class NewsArticleResponse(NewsArticleInDBBase):
    """Schema for news article responses."""
    prompt_type: str
    prompt_name: str

class NewsArticleList(BaseModel):
    """Schema for paginated news list."""
    items: List[NewsArticleResponse]
    total: int
    skip: int
    limit: int

class NewsDateResponse(BaseModel):
    """Schema for full date news response."""
    date: date
    public_news: List[NewsArticleResponse]
    internal_news: List[NewsArticleResponse]
    private_news: List[NewsArticleResponse]
    total_count: int