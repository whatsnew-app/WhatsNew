# app/schemas/task.py

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskType(str, Enum):
    NEWS_GENERATION = "news_generation"
    IMAGE_GENERATION = "image_generation"
    SYSTEM_MAINTENANCE = "system_maintenance"

class TaskBase(BaseModel):
    name: str
    type: TaskType
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    scheduled_at: Optional[datetime] = None
    is_recurring: bool = False
    cron_expression: Optional[str] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    name: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    scheduled_at: Optional[datetime] = None
    is_recurring: Optional[bool] = None
    cron_expression: Optional[str] = None

class TaskInDBBase(TaskBase):
    id: UUID
    status: TaskStatus
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)

class Task(TaskInDBBase):
    pass

class TaskResponse(TaskInDBBase):
    pass

class TaskList(BaseModel):
    tasks: list[TaskResponse]
    total: int

class TaskStatusUpdate(BaseModel):
    status: TaskStatus
    error_message: Optional[str] = None