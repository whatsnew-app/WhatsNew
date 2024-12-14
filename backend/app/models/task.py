# app/models/task.py

from uuid import UUID, uuid4
from sqlalchemy import Column, String, DateTime, Boolean, JSON, Enum, ForeignKey
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
    
    # Task details and parameters
    parameters = Column(JSON, nullable=True)
    result = Column(JSON, nullable=True)
    error_message = Column(String, nullable=True)
    
    # Scheduling and execution details
    scheduled_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    is_recurring = Column(Boolean, default=False)
    cron_expression = Column(String, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(PGUUID, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="tasks")
    
    def __repr__(self):
        return f"<Task {self.name} ({self.type}) - {self.status}>"

    def update_status(self, new_status: TaskStatus, error: str = None):
        """Update task status and relevant timestamps."""
        self.status = new_status
        self.updated_at = datetime.utcnow()
        
        if new_status == TaskStatus.IN_PROGRESS and not self.started_at:
            self.started_at = datetime.utcnow()
        elif new_status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            self.completed_at = datetime.utcnow()
            if new_status == TaskStatus.FAILED:
                self.error_message = error

        # If recurring, calculate next run time
        if self.is_recurring and self.cron_expression and new_status == TaskStatus.COMPLETED:
            # Note: You'll need to implement cron calculation logic
            pass

    def to_dict(self):
        """Convert task to dictionary for serialization."""
        return {
            "id": str(self.id),
            "name": self.name,
            "type": self.type,
            "status": self.status,
            "parameters": self.parameters,
            "result": self.result,
            "error_message": self.error_message,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "next_run_at": self.next_run_at.isoformat() if self.next_run_at else None,
            "is_recurring": self.is_recurring,
            "cron_expression": self.cron_expression,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": str(self.created_by) if self.created_by else None
        }