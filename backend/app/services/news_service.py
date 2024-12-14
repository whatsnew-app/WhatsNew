from typing import List, Optional
from datetime import datetime, date
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.news import NewsArticle
from app.models.prompt import Prompt, PromptType
from app.schemas.news import NewsArticleCreate
from app.utils.slug import generate_news_slug

class NewsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_news(self, news_in: NewsArticleCreate) -> NewsArticle:
        news = NewsArticle(**news_in.dict())
        self.db.add(news)
        await self.db.commit()
        await self.db.refresh(news)
        return news

    async def get_news_by_date(
        self,
        date: date,
        user_id: Optional[UUID] = None
    ) -> List[NewsArticle]:
        query = (
            select(NewsArticle)
            .join(Prompt)
            .where(NewsArticle.published_date.cast(date) == date)
        )
        
        if user_id:
            query = query.where(
                (Prompt.type == PromptType.PUBLIC) |
                (Prompt.type == PromptType.INTERNAL) |
                ((Prompt.type == PromptType.PRIVATE) & (Prompt.user_id == user_id))
            )
        else:
            query = query.where(Prompt.type == PromptType.PUBLIC)
        
        news = await self.db.scalars(query)
        return news.all()

    async def regenerate_slug(self, article_id: UUID) -> NewsArticle:
        news = await self.db.get(NewsArticle, article_id)
        if not news:
            raise ValueError("News article not found")
        
        new_slug = await generate_news_slug(
            news.title,
            news.prompt.name,
            news.published_date
        )
        news.slug = new_slug
        await self.db.commit()
        return news