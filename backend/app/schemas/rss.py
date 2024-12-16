# app/schemas/rss.py

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field

class RSSItemBase(BaseModel):
    title: str
    link: HttpUrl
    description: Optional[str] = None
    published_date: datetime
    content: Optional[str] = None
    author: Optional[str] = None
    categories: List[str] = []

class RSSFeedContent(BaseModel):
    title: str
    link: HttpUrl
    description: Optional[str] = None
    items: List[RSSItemBase]
    last_updated: datetime

class AggregatedContent(BaseModel):
    articles: List[Dict[str, Any]] = Field(
        description="List of processed articles with content and metadata"
    )
    sources: List[str] = Field(
        description="List of source URLs that were successfully processed"
    )
    failed_sources: List[str] = Field(
        description="List of source URLs that failed processing"
    )
    metadata: Dict[str, Any] = Field(
        description="Additional metadata about the aggregation process"
    )