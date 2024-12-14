# app/tasks/news_generator.py

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import asyncio
import logging

from app.models.prompt import Prompt
from app.models.news import NewsArticle
from app.models.task import Task, TaskStatus
from app.services.rss_service import RSSService
from app.services.llm_service import LLMService
from app.services.image_service import ImageService
from app.services.content_processor import ContentProcessor
from app.utils.slug import generate_news_slug

logger = logging.getLogger(__name__)

class NewsGenerator:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.rss_service = RSSService()
        self.llm_service = LLMService()
        self.image_service = ImageService()
        self.content_processor = ContentProcessor()

    async def generate_news_for_prompt(self, prompt: Prompt) -> List[NewsArticle]:
        """Generate news articles for a single prompt."""
        try:
            # Fetch RSS feeds
            raw_articles = await self.rss_service.fetch_feeds(prompt.news_sources)
            
            if not raw_articles:
                logger.warning(f"No articles found for prompt {prompt.id}")
                return []

            # Process and aggregate content
            processed_content = await self.content_processor.process_articles(raw_articles)
            
            # Generate news using LLM
            llm_response = await self.llm_service.generate_news(
                content=processed_content,
                prompt_content=prompt.content,
                template_content=prompt.template.template_content
            )
            
            # Generate image if required
            image_url = None
            if prompt.generate_image:
                try:
                    image_url = await self.image_service.generate_image(llm_response["title"])
                except Exception as e:
                    logger.error(f"Image generation failed for prompt {prompt.id}: {str(e)}")

            # Create news article
            news = NewsArticle(
                title=llm_response["title"],
                content=llm_response["content"],
                summary=llm_response.get("summary"),
                source_urls=[article["url"] for article in raw_articles],
                image_url=image_url,
                ai_metadata=llm_response.get("metadata"),
                published_date=datetime.utcnow(),
                prompt_id=prompt.id,
                slug=await generate_news_slug(
                    llm_response["title"],
                    prompt.name,
                    datetime.utcnow()
                )
            )
            
            self.db.add(news)
            await self.db.commit()
            await self.db.refresh(news)
            
            return news

        except Exception as e:
            logger.error(f"Error generating news for prompt {prompt.id}: {str(e)}")
            raise

    async def run_generation_task(self, task: Task) -> None:
        """Execute the news generation task."""
        try:
            # Update task status
            task.update_status(TaskStatus.IN_PROGRESS)
            await self.db.commit()

            # Get active prompts
            prompts_query = select(Prompt).where(Prompt.is_active == True)
            result = await self.db.execute(prompts_query)
            prompts = result.scalars().all()

            generated_articles = []
            
            # Generate news for each prompt
            for prompt in prompts:
                try:
                    article = await self.generate_news_for_prompt(prompt)
                    if article:
                        generated_articles.append(article)
                except Exception as e:
                    logger.error(f"Failed to generate news for prompt {prompt.id}: {str(e)}")
                    continue

            # Update task status
            task.update_status(
                TaskStatus.COMPLETED,
                result={
                    "total_prompts": len(prompts),
                    "articles_generated": len(generated_articles),
                    "completion_time": datetime.utcnow().isoformat()
                }
            )
            await self.db.commit()

        except Exception as e:
            error_msg = f"News generation task failed: {str(e)}"
            logger.error(error_msg)
            task.update_status(TaskStatus.FAILED, error=error_msg)
            await self.db.commit()
            raise