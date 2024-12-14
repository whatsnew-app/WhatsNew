# app/tasks/scheduler.py

from datetime import datetime, timedelta
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
import logging
from uuid import UUID
from croniter import croniter

from app.models.task import Task, TaskStatus, TaskType
from app.tasks.news_generator import NewsGenerator
from app.tasks.system_monitor import SystemMonitor
from app.core.config import settings

logger = logging.getLogger(__name__)

class TaskScheduler:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.is_running = False
        self.news_generator = NewsGenerator(db)
        self.system_monitor = SystemMonitor(db)

    async def schedule_task(
        self,
        task_type: TaskType,
        name: str,
        parameters: dict = None,
        cron_expression: str = None,
        scheduled_at: datetime = None
    ) -> Task:
        """Schedule a new task."""
        try:
            next_run = None
            if cron_expression:
                next_run = croniter(cron_expression, datetime.utcnow()).get_next(datetime)
            elif scheduled_at:
                next_run = scheduled_at

            task = Task(
                name=name,
                type=task_type,
                status=TaskStatus.PENDING,
                parameters=parameters or {},
                scheduled_at=next_run,
                is_recurring=bool(cron_expression),
                cron_expression=cron_expression
            )
            
            self.db.add(task)
            await self.db.commit()
            await self.db.refresh(task)
            
            return task

        except Exception as e:
            logger.error(f"Failed to schedule task: {str(e)}")
            await self.db.rollback()
            raise

    async def run_task(self, task: Task) -> None:
        """Execute a specific task."""
        try:
            if task.type == TaskType.NEWS_GENERATION:
                await self.news_generator.run_generation_task(task)
            elif task.type == TaskType.SYSTEM_MAINTENANCE:
                await self.system_monitor.run_maintenance_task(task)
            else:
                raise ValueError(f"Unknown task type: {task.type}")

        except Exception as e:
            logger.error(f"Task execution failed: {str(e)}")
            task.update_status(TaskStatus.FAILED, error=str(e))
            await self.db.commit()

    async def process_pending_tasks(self) -> None:
        """Process all pending tasks that are due."""
        try:
            # Get tasks that are due
            now = datetime.utcnow()
            query = select(Task).where(
                and_(
                    Task.status == TaskStatus.PENDING,
                    or_(
                        Task.scheduled_at <= now,
                        Task.scheduled_at.is_(None)
                    )
                )
            )
            
            result = await self.db.execute(query)
            tasks = result.scalars().all()
            
            for task in tasks:
                try:
                    await self.run_task(task)
                    
                    # Schedule next run if task is recurring
                    if task.is_recurring and task.cron_expression:
                        next_run = croniter(task.cron_expression, now).get_next(datetime)
                        new_task = await self.schedule_task(
                            task_type=task.type,
                            name=task.name,
                            parameters=task.parameters,
                            cron_expression=task.cron_expression
                        )
                        new_task.scheduled_at = next_run
                        await self.db.commit()
                
                except Exception as e:
                    logger.error(f"Failed to process task {task.id}: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Task processing failed: {str(e)}")
            raise

    async def start(self):
        """Start the task scheduler."""
        self.is_running = True
        
        # Schedule recurring tasks
        await self.schedule_task(
            task_type=TaskType.NEWS_GENERATION,
            name="Hourly News Generation",
            cron_expression=settings.NEWS_GENERATION_CRON
        )
        
        while self.is_running:
            try:
                await self.process_pending_tasks()
                
                # Run system monitoring
                await self.system_monitor.collect_metrics()
                
                # Wait for next check interval
                await asyncio.sleep(settings.TASK_CHECK_INTERVAL)
                
            except Exception as e:
                logger.error(f"Scheduler iteration failed: {str(e)}")
                await asyncio.sleep(5)  # Brief pause before retry

    def stop(self):
        """Stop the task scheduler."""
        self.is_running = False
        logger.info("Task scheduler stopped")

    async def cleanup_completed_tasks(self, days: int = 7) -> None:
        """Clean up old completed tasks."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            old_tasks = await self.db.scalars(
                select(Task).where(
                    and_(
                        Task.status.in_([TaskStatus.COMPLETED, TaskStatus.FAILED]),
                        Task.completed_at < cutoff_date
                    )
                )
            )
            
            for task in old_tasks:
                await self.db.delete(task)
            
            await self.db.commit()
            logger.info(f"Cleaned up tasks older than {days} days")
            
        except Exception as e:
            logger.error(f"Error cleaning up old tasks: {str(e)}")
            await self.db.rollback()