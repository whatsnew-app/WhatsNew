# app/tasks/system_monitor.py

import psutil
import platform
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import logging

from app.models.stats import SystemStats, DailyStats
from app.models.task import Task, TaskStatus
from app.models.user import User
from app.models.news import NewsArticle
from app.models.prompt import Prompt

logger = logging.getLogger(__name__)

class SystemMonitor:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def collect_system_metrics(self) -> dict:
        """Collect current system metrics."""
        return {
            "cpu_usage": psutil.cpu_percent(interval=1),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "system_load": psutil.getloadavg()[0],  # 1 minute load average
            "platform": platform.platform(),
            "python_version": platform.python_version()
        }

    async def collect_user_stats(self) -> dict:
        """Collect user statistics."""
        total_users_query = select(func.count(User.id))
        active_users_query = select(func.count(User.id)).where(User.is_active == True)
        
        total_users = await self.db.scalar(total_users_query)
        active_users = await self.db.scalar(active_users_query)
        
        return {
            "total_users": total_users,
            "active_users": active_users
        }

    async def collect_content_stats(self) -> dict:
        """Collect content statistics."""
        now = datetime.utcnow()
        day_ago = now - timedelta(days=1)
        
        total_prompts_query = select(func.count(Prompt.id))
        active_prompts_query = select(func.count(Prompt.id)).where(Prompt.is_active == True)
        total_news_query = select(func.count(NewsArticle.id))
        recent_news_query = select(func.count(NewsArticle.id)).where(NewsArticle.created_at >= day_ago)
        
        stats = await asyncio.gather(
            self.db.scalar(total_prompts_query),
            self.db.scalar(active_prompts_query),
            self.db.scalar(total_news_query),
            self.db.scalar(recent_news_query)
        )
        
        return {
            "total_prompts": stats[0],
            "active_prompts": stats[1],
            "total_news_articles": stats[2],
            "articles_last_24h": stats[3]
        }

    async def collect_task_stats(self) -> dict:
        """Collect task statistics."""
        tasks_query = select(
            func.count(Task.id),
            func.count(Task.id).filter(Task.status == TaskStatus.PENDING),
            func.count(Task.id).filter(Task.status == TaskStatus.FAILED),
            func.count(Task.id).filter(Task.status == TaskStatus.COMPLETED)
        )
        
        result = await self.db.execute(tasks_query)
        total, pending, failed, completed = result.first()
        
        return {
            "total_tasks": total,
            "pending_tasks": pending,
            "failed_tasks": failed,
            "completed_tasks": completed
        }

    async def store_system_stats(self) -> SystemStats:
        """Store current system statistics."""
        try:
            metrics = await self.collect_system_metrics()
            user_stats = await self.collect_user_stats()
            content_stats = await self.collect_content_stats()
            task_stats = await self.collect_task_stats()
            
            stats = SystemStats(
                timestamp=datetime.utcnow(),
                system_metrics=metrics,
                total_users=user_stats["total_users"],
                active_users=user_stats["active_users"],
                total_prompts=content_stats["total_prompts"],
                active_prompts=content_stats["active_prompts"],
                total_news_articles=content_stats["total_news_articles"],
                articles_last_24h=content_stats["articles_last_24h"],
                pending_tasks=task_stats["pending_tasks"],
                failed_tasks=task_stats["failed_tasks"],
                completed_tasks=task_stats["completed_tasks"],
                system_load=metrics["system_load"],
                memory_usage=metrics["memory_usage"]
            )
            
            self.db.add(stats)
            await self.db.commit()
            await self.db.refresh(stats)
            
            return stats

        except Exception as e:
            logger.error(f"Failed to store system stats: {str(e)}")
            raise

    async def update_daily_stats(self) -> DailyStats:
        """Update daily statistics."""
        today = datetime.utcnow().date()
        
        try:
            daily_stats = await DailyStats.get_or_create(self.db, today)
            
            # Update daily metrics
            content_stats = await self.collect_content_stats()
            system_metrics = await self.collect_system_metrics()
            
            daily_stats.articles_generated = content_stats["articles_last_24h"]
            daily_stats.cpu_usage_avg = system_metrics["cpu_usage"]
            daily_stats.memory_usage_avg = system_metrics["memory_usage"]
            daily_stats.disk_usage_avg = system_metrics["disk_usage"]
            
            await self.db.commit()
            await self.db.refresh(daily_stats)
            
            return daily_stats

        except Exception as e:
            logger.error(f"Failed to update daily stats: {str(e)}")
            raise