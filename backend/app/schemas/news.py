# app/schemas/news.py

from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, field_serializer
from enum import Enum

class NewsArticleBase(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    source_urls: List[str]
    image_url: Optional[str] = None
    ai_metadata: Optional[Dict[str, Any]] = None

class NewsArticleCreate(NewsArticleBase):
    prompt_id: UUID
    published_date: datetime

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
    published_date: datetime
    slug: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('id', 'prompt_id')
    def serialize_uuid(self, uuid: UUID, _info):
        return str(uuid)

    @field_serializer('published_date', 'created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime, _info):
        return dt.isoformat()

class NewsArticle(NewsArticleInDBBase):
    """Schema for news article responses."""
    pass

class NewsArticleResponse(NewsArticleInDBBase):
    """Schema for detailed news article responses."""
    prompt_type: str
    prompt_name: str

class NewsArticleList(BaseModel):
    """Schema for paginated news list."""
    items: List[NewsArticleResponse]
    total: int
    skip: int
    limit: int

class NewsDateResponse(BaseModel):
    """Schema for all news articles on a specific date."""
    date: datetime
    public_news: List[NewsArticleResponse]
    internal_news: List[NewsArticleResponse]
    private_news: List[NewsArticleResponse]
    total_count: int

    @field_serializer('date')
    def serialize_datetime(self, dt: datetime, _info):
        return dt.isoformat()

class NewsStats(BaseModel):
    """Schema for news statistics."""
    total_articles: int
    articles_last_24h: int
    articles_by_type: Dict[str, int]
    average_length: Optional[float]
    generation_times: Dict[str, float]

class NewsFilter(BaseModel):
    """Schema for news filtering options."""
    date_from: Optional[datetime]
    date_to: Optional[datetime]
    prompt_types: Optional[List[str]]
    prompt_ids: Optional[List[UUID]]
    search_term: Optional[str]

    @field_serializer('prompt_ids')
    def serialize_uuids(self, prompt_ids: Optional[List[UUID]], _info):
        if prompt_ids is None:
            return None
        return [str(uuid) for uuid in prompt_ids]

    @field_serializer('date_from', 'date_to')
    def serialize_datetime(self, dt: Optional[datetime], _info):
        if dt is None:
            return None
        return dt.isoformat()

class NewsInDB(NewsArticleInDBBase):
    """Schema for news article in database."""
    pass