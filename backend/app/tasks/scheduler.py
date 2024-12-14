# app/tasks/scheduler.py

from datetime import datetime, timedelta
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
from croniter import croniter

from app.models.task import Task, TaskStatus, TaskType
from app.tasks.news_generator import NewsGenerator
from app.tasks.system_monitor import SystemMonitor

logger = logging.getLogger(__name__)

class TaskScheduler:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.is_running = False
        self.news_generator = NewsGenerator(db)
        self.system_monitor = SystemMonitor(db)

    async def schedule_task(self, task_type: TaskType, name: str, cron_expression: str = None, 
                          parameters: dict = None) -> Task:
        """Schedule a new task."""
        try:
            next_run = None
            if cron_expression:
                next_run = croniter(cron_expression, datetime.utcnow()).get_next(datetime)

            task = Task(
                name=name,
                type=task_type,
                status=TaskStatus.PENDING,
                parameters=parameters,
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
            raise

    async def run_task(self, task: Task) -> None:
        """Execute a specific task."""
        try:
            if task.type == TaskType.NEWS_GENERATION:
                await self.news_generator.run_generation_task(task)
            else:
                raise ValueError(f"Unknown task type: {task.type}")

        except Exception as e:
            logger.error(f"Task execution failed: {str(e)}")
            task.update_status(TaskStatus.FAILED, error=str(e))
            await self.db.commit()

    async def process_pending_tasks(self) -> None:
        """Process all pending tasks that are due."""
        try:
            now = datetime.utcnow()
            query = select(Task).where(
                (Task.status == TaskStatus.PENDING) &
                ((Task.scheduled_at <= now) | (Task.scheduled_at == None))
            )
            
            result = await self.db.execute(query)
            tasks = result.scalars().all()
            
            for task in tasks:
                try:
                    await self.run_task(task)
                    
                    # If task is recurring, schedule next run
                    if task.is_recurring and task.cron_expression:
                        next_run = croniter(task.cron_expression, now).get_next(datetime)
                        new_task = await self.schedule_task(
                            task_type=task.type,
                            name=task.name,
                            cron_expression=task.cron_expression,
                            parameters=task.parameters
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
        
        while self.is_running:
            try:
                await self.process_pending_tasks()
                # Schedule system monitoring
                await self.system_monitor.store_system_stats()
                await self.system_monitor.update_daily_stats()
                
                # Wait for next interval
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Scheduler iteration failed: {str(e)}")
                await asyncio.sleep(5)  # Wait before retrying

    def stop(self):
        """Stop the task scheduler."""
        self.is_running = False