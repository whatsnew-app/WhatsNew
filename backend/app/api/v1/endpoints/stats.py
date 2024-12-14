# app/api/v1/endpoints/stats.py

from typing import Dict, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_superuser
from app.models.news import NewsArticle
from app.models.prompt import Prompt
from app.models.user import User

router = APIRouter()

@router.get(
    "/admin/stats",
    dependencies=[Depends(get_current_superuser)]
)
async def get_system_stats(
    db: AsyncSession = Depends(get_db)
):
    """Get system statistics including user counts, prompt counts, and news generation metrics."""
    
    # Get user statistics
    user_query = select(
        func.count(User.id).label('total_users'),
        func.count(User.id).filter(User.is_active == True).label('active_users')
    )
    user_result = await db.execute(user_query)
    user_stats = user_result.mappings().first()
    
    # Get prompt statistics
    prompt_query = select(
        func.count(Prompt.id).label('total_prompts'),
        func.sum(case((Prompt.type == 'public', 1), else_=0)).label('public_prompts'),
        func.sum(case((Prompt.type == 'private', 1), else_=0)).label('private_prompts'),
        func.sum(case((Prompt.type == 'internal', 1), else_=0)).label('internal_prompts')
    )
    prompt_result = await db.execute(prompt_query)
    prompt_stats = prompt_result.mappings().first()
    
    # Get news article statistics for the last 24 hours
    yesterday = datetime.utcnow() - timedelta(days=1)
    news_query = select(
        func.count(NewsArticle.id).label('total_articles'),
        func.count(NewsArticle.id).filter(
            NewsArticle.created_at >= yesterday
        ).label('articles_last_24h')
    )
    news_result = await db.execute(news_query)
    news_stats = news_result.mappings().first()
    
    return {
        "user_statistics": {
            "total_users": user_stats.total_users,
            "active_users": user_stats.active_users,
            "inactive_users": user_stats.total_users - user_stats.active_users
        },
        "prompt_statistics": {
            "total_prompts": prompt_stats.total_prompts,
            "public_prompts": prompt_stats.public_prompts,
            "private_prompts": prompt_stats.private_prompts,
            "internal_prompts": prompt_stats.internal_prompts
        },
        "news_statistics": {
            "total_articles": news_stats.total_articles,
            "articles_last_24h": news_stats.articles_last_24h,
            "generation_rate": f"{news_stats.articles_last_24h / 24:.2f} articles/hour"
        },
        "system_status": {
            "last_updated": datetime.utcnow().isoformat(),
            "status": "healthy"
        }
    }

@router.get(
    "/admin/stats/daily",
    dependencies=[Depends(get_current_superuser)]
)
async def get_daily_stats(
    days: int = 7,
    db: AsyncSession = Depends(get_db)
):
    """Get daily statistics for the specified number of days."""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get daily news article counts
    daily_news_query = select(
        func.date(NewsArticle.created_at).label('date'),
        func.count(NewsArticle.id).label('article_count')
    ).where(
        NewsArticle.created_at >= start_date
    ).group_by(
        func.date(NewsArticle.created_at)
    ).order_by(
        func.date(NewsArticle.created_at)
    )
    
    daily_news_result = await db.execute(daily_news_query)
    daily_stats = [
        {
            "date": str(row.date),
            "article_count": row.article_count
        }
        for row in daily_news_result
    ]
    
    return {
        "daily_statistics": daily_stats,
        "period": {
            "start_date": start_date.date().isoformat(),
            "end_date": datetime.utcnow().date().isoformat(),
            "days": days
        }
    }