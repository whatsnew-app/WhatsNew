# app/tasks/news_generator.py

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy import text
import logging
import asyncio
from app.models.ai_config import LLMConfig, ImageConfig
from app.models.prompt import Prompt
from app.models.task import Task, TaskStatus, TaskType
from app.models.news import NewsArticle
from app.services.content_processor import ContentProcessor
from app.services.llm_service import LLMService
from app.services.image_service import ImageService
from app.core.config import settings

logger = logging.getLogger(__name__)

class NewsGenerator:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.content_processor = None

    async def initialize_services(self):
        """Initialize required services."""
        # Get default LLM config
        llm_config = await self.db.scalar(
            select(LLMConfig).where(LLMConfig.is_default == True)
        )
        if not llm_config:
            raise ValueError("No default LLM configuration found")

        # Get default image config
        image_config = await self.db.scalar(
            select(ImageConfig).where(ImageConfig.is_default == True)
        )
        if not image_config:
            raise ValueError("No default image configuration found")

        logger.info(f"Using LLM config: {llm_config.id} with API key: {llm_config.api_key[:8]}...")
        
        # Initialize services
        llm_service = LLMService(llm_config)
        image_service = ImageService(image_config)
        self.content_processor = ContentProcessor(self.db, llm_service, image_service)

    async def generate_news_for_prompt(
        self,
        prompt: Prompt,
        task: Optional[Task] = None
    ) -> NewsArticle:
        """Generate news for a single prompt."""
        try:
            if not self.content_processor:
                await self.initialize_services()

            # Create a local task variable if it doesn't exist
            current_task = task
            
            article = await self.content_processor.process_prompt(
                prompt=prompt,
                task_id=current_task.id if current_task else None
            )
            return article

        except Exception as e:
            error_msg = f"Error processing prompt {prompt.id}: {str(e)}"
            logger.error(error_msg)
            if current_task:  # Use the local variable here
                current_task.error_message = error_msg
                await self.db.commit()
            raise ValueError(error_msg)

    async def run_generation_task(self, task: Task) -> None:
        """Execute the news generation task."""
        try:
            # Initialize services first
            if not self.content_processor:
                await self.initialize_services()

            # Update task status
            task.update_status(TaskStatus.IN_PROGRESS)
            task.started_at = datetime.utcnow()
            await self.db.commit()

            # Get active prompts
            query = select(Prompt).where(
                and_(
                    Prompt.is_active == True,
                    or_(
                        Prompt.last_run_at.is_(None),
                        Prompt.last_run_at <= func.now() - text("interval '1 hour'")
                    )
                )
            )
            result = await self.db.execute(query)
            prompts = result.scalars().all()

            if not prompts:
                logger.info("No prompts to process")
                task.update_status(
                    TaskStatus.COMPLETED,
                    result={"message": "No prompts to process"}
                )
                await self.db.commit()
                return

            # Process prompts
            results = {
                "successful": [],
                "failed": [],
                "total_prompts": len(prompts)
            }

            for prompt in prompts:
                try:
                    article = await self.generate_news_for_prompt(prompt, task)
                    if article:
                        results["successful"].append(str(article.id))
                        prompt.last_run_at = func.now()
                        await self.db.commit()
                except Exception as e:
                    error_msg = f"Error generating news for prompt {prompt.id}: {str(e)}"
                    logger.error(error_msg)
                    results["failed"].append({
                        "prompt_id": str(prompt.id),
                        "error": error_msg
                    })
                    continue  # Continue with next prompt even if one fails

            # Update task completion
            completion_time = datetime.utcnow()
            task.update_status(
                TaskStatus.COMPLETED,
                result={
                    "successful_count": len(results["successful"]),
                    "failed_count": len(results["failed"]),
                    "total_prompts": len(prompts),
                    "completion_time": completion_time.isoformat(),
                    "details": results
                }
            )
            await self.db.commit()

        except Exception as e:
            error_msg = f"News generation task failed: {str(e)}"
            logger.error(error_msg)
            task.update_status(TaskStatus.FAILED, error=error_msg)
            await self.db.commit()
            
            raise

    async def cleanup_old_articles(self, days: int = 30) -> None:
        """Clean up old articles to prevent database bloat."""
        try:
            # Use PostgreSQL's interval for date comparison
            old_articles = await self.db.scalars(
                select(NewsArticle)
                .where(NewsArticle.created_at <= func.now() - func.interval(f'{days} days'))
            )
            
            for article in old_articles:
                await self.db.delete(article)
            
            await self.db.commit()
            logger.info(f"Cleaned up articles older than {days} days")
            
        except Exception as e:
            logger.error(f"Error cleaning up old articles: {str(e)}")
            await self.db.rollback()