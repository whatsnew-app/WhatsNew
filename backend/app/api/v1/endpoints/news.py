# app/api/v1/endpoints/news.py

from datetime import date, datetime
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from app.api.deps import get_db, get_current_active_user
from app.models.news import NewsArticle
from app.models.prompt import Prompt, PromptType
from app.models.user import User
from app.schemas.news import (
    NewsArticleResponse,
    NewsArticleList,
    NewsDateResponse
)

router = APIRouter()

@router.get("/my", response_model=NewsArticleList)
async def get_my_news(
    skip: int = 0,
    limit: int = 20,
    date_filter: date | None = None,
    prompt_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> NewsArticleList:
    """Get news articles from user's prompts."""
    # Build base query
    base_query = (
        select(NewsArticle)
        .join(Prompt)
        .where(Prompt.user_id == current_user.id)
    )
    
    if date_filter:
        base_query = base_query.where(NewsArticle.published_date.cast(date) == date_filter)
    if prompt_id:
        base_query = base_query.where(NewsArticle.prompt_id == prompt_id)
    
    # Get total count
    count_query = select(func.count()).select_from(NewsArticle).join(Prompt).where(Prompt.user_id == current_user.id)
    if date_filter:
        count_query = count_query.where(NewsArticle.published_date.cast(date) == date_filter)
    if prompt_id:
        count_query = count_query.where(NewsArticle.prompt_id == prompt_id)
    
    total = await db.scalar(count_query)
    
    # Add pagination
    query = base_query.offset(skip).limit(limit)
    result = await db.execute(query)
    articles = result.scalars().all()
    
    return NewsArticleList(
        items=articles,
        total=total,
        skip=skip,
        limit=limit
    )

@router.get("/private/{prompt_name}/{date}/{slug}", response_model=NewsArticleResponse)
async def get_private_news(
    prompt_name: str,
    date_filter: date,
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> NewsArticle:
    """Get a specific private news article."""
    article = await db.scalar(
        select(NewsArticle)
        .join(Prompt)
        .where(
            Prompt.name == prompt_name,
            NewsArticle.published_date.cast(date) == date_filter,
            NewsArticle.slug == slug,
            Prompt.type == PromptType.PRIVATE
        )
    )
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Check ownership
    if article.prompt.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this article"
        )
    
    return article

@router.get("/{date}/full", response_model=NewsDateResponse)
async def get_full_news(
    date_filter: date,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> NewsDateResponse:
    """Get all accessible news for a specific date."""
    # Build query for accessible news
    query = (
        select(NewsArticle)
        .join(Prompt)
        .where(NewsArticle.published_date.cast(date) == date_filter)
        .where(
            (Prompt.type == PromptType.PUBLIC) |
            (Prompt.type == PromptType.INTERNAL) |
            ((Prompt.type == PromptType.PRIVATE) & (Prompt.user_id == current_user.id))
        )
    )
    
    result = await db.execute(query)
    articles = result.scalars().all()
    
    # Organize articles by type
    public_news = [a for a in articles if a.prompt.type == PromptType.PUBLIC]
    internal_news = [a for a in articles if a.prompt.type == PromptType.INTERNAL]
    private_news = [a for a in articles if a.prompt.type == PromptType.PRIVATE]
    
    return NewsDateResponse(
        date=date_filter,
        public_news=public_news,
        internal_news=internal_news,
        private_news=private_news,
        total_count=len(articles)
    )