# app/services/content_processor.py

from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from uuid import UUID
from sqlalchemy import func
from sqlalchemy import select
from app.models.prompt_template import PromptTemplate
from app.services.source_aggregator import SourceAggregator
from app.services.llm_service import LLMService
from app.services.image_service import ImageService
from app.models.news import NewsArticle
from app.models.prompt import Prompt, PromptType
from app.models.task import Task, TaskStatus
from app.utils.slug import generate_news_slug
from app.api.v1.endpoints.websocket import broadcast_new_article
from app.schemas.news import NewsArticleResponse

logger = logging.getLogger(__name__)

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

    async def process_prompt(
        self,
        prompt: Prompt,
        task_id: Optional[UUID] = None
    ) -> NewsArticle:
        """Process a prompt and create a news article with task tracking."""
        task = None
        try:
            # Get current time once
            current_time = datetime.utcnow().replace(tzinfo=None)

            # Load template explicitly
            template = await self.db.scalar(
                select(PromptTemplate).where(PromptTemplate.id == prompt.template_id)
            )
            if not template:
                raise ValueError(f"Template {prompt.template_id} not found")

            # Update task status if provided
            if task_id:
                task = await self.db.scalar(
                    select(Task).where(Task.id == task_id)
                )
                if task:
                    task.status = TaskStatus.IN_PROGRESS
                    await self.db.commit()

            # Fetch and aggregate source content
            logger.info(f"Fetching articles from sources: {prompt.news_sources}")
            articles = await self.aggregator.aggregate_sources(
                prompt.news_sources
            )
            
            if not articles:
                logger.warning(f"No articles found for prompt {prompt.id}")
                raise ValueError("No articles found from specified sources")

            logger.info(f"Found {len(articles)} articles to process")

            # Generate content using LLM with explicitly loaded template
            content_result = await self.llm_service.generate_content(
                articles,
                prompt.content,
                template.template_content
            )

            if not content_result.get('title') or not content_result.get('content'):
                raise ValueError("LLM failed to generate valid content")

            # Generate slug
            slug = await generate_news_slug(
                content_result['title'],
                prompt.name,
                current_time
            )

            # Create news article
            news = NewsArticle(
                title=content_result['title'],
                content=content_result['content'],
                summary=content_result.get('summary'),
                slug=slug,
                source_urls=[a['link'] for a in articles],
                prompt_id=prompt.id,
                published_date=current_time,
                ai_metadata={
                    **content_result['metadata'],
                    'task_id': str(task_id) if task_id else None,
                    'processing_time': current_time.isoformat(),
                    'source_count': len(articles)
                }
            )

            # Generate image if required
            if prompt.generate_image and content_result.get('image_prompt'):
                try:
                    image_result = await self.image_service.generate_image(
                        content_result['image_prompt']
                    )
                    news.image_url = image_result['url']
                    news.ai_metadata['image_generation'] = image_result['metadata']
                except Exception as e:
                    logger.error(f"Error generating image: {str(e)}")
                    news.ai_metadata['image_error'] = str(e)

            self.db.add(news)
            
            # Update prompt's last run time
            prompt.last_run_at = current_time
            
            await self.db.commit()
            await self.db.refresh(news)

            # Convert to response schema before broadcasting
            news_response = NewsArticleResponse(
                id=news.id,
                title=news.title,
                content=news.content,
                summary=news.summary,
                source_urls=news.source_urls,
                image_url=news.image_url,
                slug=news.slug,
                ai_metadata=news.ai_metadata,
                prompt_id=news.prompt_id,
                published_date=news.published_date,
                created_at=news.created_at,
                updated_at=news.updated_at,
                prompt_type=prompt.type,
                prompt_name=prompt.name
            )
            
            # Broadcast new article
            await broadcast_new_article(
                article=news_response,
                prompt_type=prompt.type,
                user_id=prompt.user_id if prompt.type == PromptType.PRIVATE else None
            )

            # Update task status if provided
            if task_id and task:
                task.status = TaskStatus.COMPLETED
                task.result = {
                    'article_id': str(news.id),
                    'completion_time': current_time.isoformat()
                }
                await self.db.commit()
            
            return news

        except Exception as e:
            logger.error(f"Error processing prompt {prompt.id}: {str(e)}")
            
            # Update task status if provided
            if task_id and task:
                task.status = TaskStatus.FAILED
                task.error_message = str(e)
                await self.db.commit()
            
            raise

    async def process_batch(
        self,
        prompts: List[Prompt],
        task_id: Optional[UUID] = None
    ) -> Dict:
        """Process multiple prompts with batch tracking."""
        results = {
            'successful': [],
            'failed': [],
            'total': len(prompts)
        }
        
        for prompt in prompts:
            try:
                article = await self.process_prompt(prompt, task_id)
                if article:
                    results['successful'].append(str(article.id))
            except Exception as e:
                logger.error(f"Error in batch processing for prompt {prompt.id}: {str(e)}")
                results['failed'].append({
                    'prompt_id': str(prompt.id),
                    'error': str(e)
                })
        
        return results