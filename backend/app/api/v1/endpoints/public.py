from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import date

from app.api.deps import get_db
from app.models.news import NewsArticle
from app.models.prompt import Prompt, PromptType
from app.schemas.news import NewsArticle as NewsArticleSchema
from app.schemas.prompt import Prompt as PromptSchema

router = APIRouter()

@router.get("/news", response_model=List[NewsArticleSchema])
async def get_public_news(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    date_filter: date = None
):
    """Get public news articles"""
    query = (
        select(NewsArticle)
        .join(Prompt)
        .where(Prompt.type == PromptType.PUBLIC)
        .order_by(NewsArticle.published_date.desc())
    )
    
    if date_filter:
        query = query.where(NewsArticle.published_date.cast(date) == date_filter)
    
    news = await db.scalars(
        query.offset(skip).limit(limit)
    )
    return news.all()

@router.get("/news/{prompt_name}/{date}/{slug}", response_model=NewsArticleSchema)
async def get_public_news_by_slug(
    prompt_name: str,
    date: date,
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific public news article by its slug"""
    full_slug = f"{prompt_name}/{date}/{slug}"
    news = await db.scalar(
        select(NewsArticle)
        .join(Prompt)
        .where(
            NewsArticle.slug == full_slug,
            Prompt.type == PromptType.PUBLIC
        )
    )
    if not news:
        raise HTTPException(status_code=404, detail="News article not found")
    return news

@router.get("/prompts", response_model=List[PromptSchema])
async def get_public_prompts(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """Get all public prompts"""
    query = (
        select(Prompt)
        .options(selectinload(Prompt.template))  # Eager load the template relationship
        .where(Prompt.type == PromptType.PUBLIC)
        .order_by(Prompt.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    
    result = await db.execute(query)
    prompts = result.scalars().all()
    return prompts