# app/models/task.py

from uuid import UUID, uuid4
from sqlalchemy import Column, String, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base

class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskType(str, enum.Enum):
    NEWS_GENERATION = "news_generation"
    IMAGE_GENERATION = "image_generation"
    SYSTEM_MAINTENANCE = "system_maintenance"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(PGUUID, primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    status = Column(String, default=TaskStatus.PENDING)
    parameters = Column(JSON, nullable=True)
    result = Column(JSON, nullable=True)
    error_message = Column(String, nullable=True)
    scheduled_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    is_recurring = Column(Boolean, default=False)
    cron_expression = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(PGUUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    def update_status(self, new_status: TaskStatus, error: str | None = None, result: dict | None = None) -> None:
        """Update task status and optionally set error message and result"""
        self.status = new_status
        if error:
            self.error_message = error
        if result:
            self.result = result
        self.updated_at = datetime.utcnow()
        
        # If the task is complete or failed, set completed_at
        if new_status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            self.completed_at = datetime.utcnow()
        
        # If the task is starting, set started_at
        if new_status == TaskStatus.IN_PROGRESS and not self.started_at:
            self.started_at = datetime.utcnow()