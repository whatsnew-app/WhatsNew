from typing import List, Dict
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.source_aggregator import SourceAggregator
from app.services.llm_service import LLMService
from app.services.image_service import ImageService
from app.models.news import NewsArticle
from app.models.prompt import Prompt
from app.utils.slug import generate_news_slug

class ContentProcessor:
    def __init__(
        self,
        db: AsyncSession,
        llm_service: LLMService,
        image_service: ImageService
    ):
        self.db = db
        self.aggregator = SourceAggregator()
        self.llm_service = llm_service
        self.image_service = image_service

    async def process_prompt(self, prompt: Prompt) -> NewsArticle:
        """Process a prompt and create a news article"""
        # Fetch and aggregate source content
        articles = await self.aggregator.aggregate_sources(
            prompt.news_sources
        )
        
        if not articles:
            return None

        # Generate content using LLM
        content_result = await self.llm_service.generate_content(
            articles,
            prompt.content,
            prompt.template.template_content
        )

        # Generate slug
        slug = await generate_news_slug(
            content_result['title'],
            prompt.name,
            datetime.utcnow()
        )

        # Create news article
        news = NewsArticle(
            title=content_result['title'],
            content=content_result['content'],
            summary=content_result['summary'],
            slug=slug,
            source_urls=[a['link'] for a in articles],
            prompt_id=prompt.id,
            published_date=datetime.utcnow(),
            ai_metadata=content_result['metadata']
        )

        # Generate image if required
        if prompt.generate_image:
            try:
                image_url = await self.image_service.generate_image(
                    content_result['image_prompt']
                )
                news.image_url = image_url
            except Exception as e:
                # Log error but continue without image
                print(f"Error generating image: {str(e)}")

        self.db.add(news)
        await self.db.commit()
        await self.db.refresh(news)
        
        return news