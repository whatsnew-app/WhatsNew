# app/services/news_service.py

from typing import List, Optional
from datetime import datetime, date
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from app.models.news import NewsArticle
from app.models.prompt import Prompt, PromptType
from app.schemas.news import NewsArticleCreate
from app.utils.slug import generate_news_slug
from app.api.v1.endpoints.websocket import broadcast_new_article

logger = logging.getLogger(__name__)

class NewsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_news(self, news_in: NewsArticleCreate) -> NewsArticle:
        """Create a news article and broadcast via WebSocket."""
        try:
            news = NewsArticle(**news_in.dict())
            self.db.add(news)
            await self.db.commit()
            await self.db.refresh(news)
            
            # Broadcast new article via WebSocket
            await broadcast_new_article(
                article=news,
                prompt_type=news.prompt.type,
                user_id=news.prompt.user_id if news.prompt.type == PromptType.PRIVATE else None
            )
            
            return news
            
        except Exception as e:
            logger.error(f"Error creating news article: {str(e)}")
            await self.db.rollback()
            raise

    async def get_news_by_date(
        self,
        date: date,
        user_id: Optional[UUID] = None
    ) -> List[NewsArticle]:
        """Get news articles for a specific date."""
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

    async def get_news_for_processing(self, hours_back: int = 24) -> List[NewsArticle]:
        """Get recent news articles for task processing."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        query = (
            select(NewsArticle)
            .where(NewsArticle.published_date >= cutoff_time)
            .order_by(NewsArticle.published_date.desc())
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def regenerate_slug(self, article_id: UUID) -> NewsArticle:
        """Regenerate slug for a news article."""
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

    async def process_batch(
        self,
        articles: List[NewsArticle],
        task_id: Optional[UUID] = None
    ) -> dict:
        """Process a batch of news articles with task tracking."""
        try:
            processed_count = 0
            error_count = 0
            
            for article in articles:
                try:
                    # Process individual article
                    # Add any additional processing logic here
                    processed_count += 1
                except Exception as e:
                    logger.error(f"Error processing article {article.id}: {str(e)}")
                    error_count += 1
            
            return {
                "processed_count": processed_count,
                "error_count": error_count,
                "task_id": task_id
            }
            
        except Exception as e:
            logger.error(f"Batch processing error: {str(e)}")
            raise