from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, date
from uuid import UUID

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.news import NewsArticle
from app.models.prompt import Prompt, PromptType
from app.schemas.news import (
    NewsArticle as NewsArticleSchema,
    NewsArticleCreate,
    NewsArticleUpdate
)
from app.utils.slug import generate_news_slug

router = APIRouter()

@router.get("/public", response_model=List[NewsArticleSchema])
async def get_public_news(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 20,
    date: Optional[date] = None
):
    query = (
        select(NewsArticle)
        .join(Prompt)
        .where(Prompt.type == PromptType.PUBLIC)
    )
    
    if date:
        query = query.where(NewsArticle.published_date.cast(date) == date)
    
    news = await db.scalars(
        query.offset(skip).limit(limit)
    )
    return news.all()

@router.get("/my", response_model=List[NewsArticleSchema])
async def get_my_news(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    query = (
        select(NewsArticle)
        .join(Prompt)
        .where(Prompt.user_id == current_user.id)
    )
    
    news = await db.scalars(
        query.offset(skip).limit(limit)
    )
    return news.all()

@router.get("/{prompt_name}/{date}/{slug}", response_model=NewsArticleSchema)
async def get_news_by_slug(
    prompt_name: str,
    date: date,
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    query = (
        select(NewsArticle)
        .join(Prompt)
        .where(
            NewsArticle.slug == f"{prompt_name}/{date}/{slug}"
        )
    )
    
    news = await db.scalar(query)
    if not news:
        raise HTTPException(status_code=404, detail="News article not found")
    
    # Check permissions
    if news.prompt.type == PromptType.PRIVATE:
        if not current_user or news.prompt.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    elif news.prompt.type == PromptType.INTERNAL and not current_user:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return news