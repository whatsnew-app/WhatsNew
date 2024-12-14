# app/api/v1/endpoints/tasks.py

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.api.deps import get_db, get_current_superuser
from app.models.task import Task, TaskType, TaskStatus
from app.models.user import User
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskList,
    TaskStatusUpdate
)
from app.tasks.scheduler import TaskScheduler

router = APIRouter()

@router.post(
    "/admin/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_superuser)]
)
async def create_task(
    task: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Create a new task."""
    scheduler = TaskScheduler(db)
    
    db_task = await scheduler.schedule_task(
        task_type=task.type,
        name=task.name,
        cron_expression=task.cron_expression,
        parameters=task.parameters
    )
    
    return db_task

@router.get(
    "/admin/tasks",
    response_model=TaskList,
    dependencies=[Depends(get_current_superuser)]
)
async def list_tasks(
    skip: int = 0,
    limit: int = 100,
    task_type: TaskType = None,
    status: TaskStatus = None,
    db: AsyncSession = Depends(get_db)
):
    """List all tasks with optional filtering."""
    query = select(Task)
    
    if task_type:
        query = query.filter(Task.type == task_type)
    if status:
        query = query.filter(Task.status == status)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    total_query = select(func.count(Task.id))
    if task_type:
        total_query = total_query.filter(Task.type == task_type)
    if status:
        total_query = total_query.filter(Task.status == status)
    
    total = await db.scalar(total_query)
    
    return TaskList(tasks=tasks, total=total)

@router.get(
    "/admin/tasks/{task_id}",
    response_model=TaskResponse,
    dependencies=[Depends(get_current_superuser)]
)
async def get_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific task."""
    task = await db.scalar(select(Task).filter(Task.id == task_id))
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task

@router.put(
    "/admin/tasks/{task_id}/status",
    response_model=TaskResponse,
    dependencies=[Depends(get_current_superuser)]
)
async def update_task_status(
    task_id: UUID,
    status_update: TaskStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update task status."""
    task = await db.scalar(select(Task).filter(Task.id == task_id))
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    task.update_status(status_update.status, status_update.error_message)
    await db.commit()
    await db.refresh(task)
    return task

@router.post(
    "/admin/tasks/news-generation",
    response_model=TaskResponse,
    dependencies=[Depends(get_current_superuser)]
)
async def trigger_news_generation(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Manually trigger news generation task."""
    scheduler = TaskScheduler(db)
    
    task = await scheduler.schedule_task(
        task_type=TaskType.NEWS_GENERATION,
        name="Manual News Generation",
        parameters={"triggered_by": str(current_user.id)}
    )
    
    background_tasks.add_task(scheduler.run_task, task)
    return task

@router.delete(
    "/admin/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_superuser)]
)
async def delete_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete a task."""
    task = await db.scalar(select(Task).filter(Task.id == task_id))
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    await db.delete(task)
    await db.commit()
    return None